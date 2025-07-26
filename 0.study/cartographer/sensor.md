# sensor

* 感知数据定义(PointCloud,Imu,Odometry,...)
* 数据容器（Collector,TrajectoryCollator）

[toc]

## 数据类型定义 及 Proto转换

* **point_cloud.h** PointCloud ： 点云数据
* **odometry_data.h** OdometryData ： 里程计数据
* **imu_data.h** ImuData ： 陀螺仪数据
* **fixed_frame_pose_data.h** FixedFramePoseData ： 固定帧位姿数据。用于存储类似于GPS或固定位置的数据， 数据将在**优化**过程中使用。

* **timed_point_cloud_data.h** TimedPointCloudData ： 每个点都带时间 点云数据
* **range_data.h** RangeData ： lidar数据，区分misses点，根据代码注释，后面会去掉missess数据

```c++
struct RangeData {
  Eigen::Vector3f origin;   // 射线起点坐标
  PointCloud returns;       // 检测到障碍物的点云
  PointCloud misses;        // 无障碍物区域的点云
};

///cartographer/mapping/internal/3d/local_trajectory_builder_3d.cc

// TODO(wohe): since `misses` are not used anywhere in 3D, consider
          // removing `misses` from `range_data` and/or everywhere in 3D.
          misses.push_back(sensor::RangefinderPoint{
              origin_in_local + options_.max_range() / range * delta});
```

* **map_by_time.h** MapByTime ： 按时间顺序管理轨迹数据​​的模板类
  * Append(trajectory_id，Data) 必须按时间严格递增 添加数据
  * Trim(nodes,node_id)当节点 (node_id) 被移除时，清理关联轨迹的无效数据

```c++
// { trajectory_id , { time,data } }
std::map<int, std::map<common::Time, DataType>> data_;
```

* **landmark_data.h** LandmarkData ：地标数据

```c++
struct LandmarkObservation {
  std::string id;  // 地标唯一标识符
  transform::Rigid3d landmark_to_tracking_transform;  // 地标->跟踪系的刚体变换
  double translation_weight;  // 平移分量的优化权重
  double rotation_weight;    // 旋转分量的优化权重
};
```

* compressed_point_cloud.h:  点云压缩类;
  * 目的：压缩ponits以减少存储空间, 有精度损失;
  * 精度定义: constexpr float kPrecision = 0.001f;  // in meters.


## data 关系类图

![类图](./assets/puml/sensor/data.puml)

```c++
/// cartographer/sensor/internal/dispatchable.h
/// 用unique_ptr 创建一个可被分派的数据对象(ImuData,PointcloudData,...)
template <typename DataType>
std::unique_ptr<Dispatchable<DataType>> MakeDispatchable(
    const std::string &sensor_id, const DataType &data) {
  return absl::make_unique<Dispatchable<DataType>>(sensor_id, data);
}
```

## Collator

> Collator 在map_builder 初始化时创建

```c++
/// cartographer/mapping/map_builder.cc
  if (options.collate_by_trajectory()) {
    sensor_collator_ = absl::make_unique<sensor::TrajectoryCollator>();
  } else {
    sensor_collator_ = absl::make_unique<sensor::Collator>();
  }
```

## TrajectoryCollator 和 Collator 区别

* **TrajectoryCollator** 按 trajectory_id 创建独立的`OrderedMultiQueue`实例；
* **TrajectoryCollator**包含 指标监控系统(**metrics**)

### 多队列管理策略

* **TrajectoryCollator**：为每个轨迹(trajectory)创建独立的`OrderedMultiQueue`实例

  ```cpp
  std::map<int, OrderedMultiQueue> trajectory_to_queue_;
  ```

* **Collator**：使用全局单一的`OrderedMultiQueue`管理所有轨迹的数据

  ```cpp
  OrderedMultiQueue queue_;  // 全局统一队列
  ```

### 指标统计功能

* **TrajectoryCollator**包含 指标监控系统：
  * 注册指标族：

  ```cpp
  metrics::Family<metrics::Counter>* collator_metrics_family_;
  ```

  * 数据计数：

  ```cpp
  auto* metric = GetOrCreateSensorMetric(data->GetSensorId(), trajectory_id);
  metric->Increment();
  ```

* 按(sensor_id, trajectory_id)维度统计
* **Collator**没有实现任何指标监控


## voxel_filter.h （体素滤波）

**点云体素滤波（Voxel Filter）**，用于SLAM中的点云降采样。核心思想是将点云划分成规则的三维网格（体素），每个网格内仅保留一个点，以此降低数据量同时保留几何结构特征。

---

### **关键函数分析**

1. **`FilterByMaxRange()`**
   * **作用**：过滤超出指定最大距离的点
   * **逻辑**：遍历点云，保留所有 `position.norm() <= max_range` 的点
   * **目的**：预处理点云，移除过远的噪声点或无效点

2. **`AdaptivelyVoxelFiltered()`**
   * **作用**：**自适应体素滤波**
   * **核心逻辑**：
     * 若原始点数 ≤ `min_num_points`，直接返回原数据（已足够稀疏）
     * 先用 `max_length` 滤波：
       * 结果点数 ≥ `min_num_points` → 返回结果
     * 若不足，则二分搜索最佳体素尺寸（`low_length`）：
       * 在 [`max_length`， `0.01 * max_length`] 间搜索
       * 确保结果点数 ≥ `min_num_points`
       * 当尺寸误差 ≤ 10% 时停止搜索
   * **优势**：动态平衡点云密度与计算效率

3. **`GetVoxelCellIndex()`**
   * **作用**：计算点所属体素的唯一索引
   * **方法**：
     * 坐标除以 `resolution` 并四舍五入到整数
     * 通过位操作（`x << 42 | y << 21 | z`）生成64位唯一键
   * **意义**：快速将点映射到哈希表

4. **`RandomizedVoxelFilterIndices()`**
   * **作用**：**随机化体素滤波（核心算法）**
   * **步骤**：
     * 遍历点云，计算每个点的 `VoxelKeyType`
     * 用**蓄水池采样（Reservoir Sampling）** 记录当前体素内随机选中的点索引
     * 返回布尔数组标记保留的点
   * **优势**：每个体素内随机保留一点，避免固定位置采样偏差

5. **`VoxelFilter()` 重载**
   * **作用**：对不同类型点云进行体素滤波
   * **实现方式**：
     * `std::vector<RangefinderPoint>`：调用 `RandomizedVoxelFilter()`
     * `PointCloud`：
       * 用 `RandomizedVoxelFilterIndices()` 获取保留标记
       * **同步处理强度值**：只保留对应点的强度
     * `TimedPointCloud` / `RangeMeasurement`：类似点滤波，额外处理时间信息

6. **`CreateAdaptiveVoxelFilterOptions()`**
   * **作用**：从Lua配置创建自适应滤波参数
   * **参数**：
     * `max_length`：初始最大体素尺寸
     * `min_num_points`：最小保留点数阈值
     * `max_range`：点云距离截断值

7. **`AdaptiveVoxelFilter()`**
   * **作用**：自适应体素滤波的对外接口
   * **流程**：
     * 先调用 `FilterByMaxRange()` 截断远点
     * 再调用 `AdaptivelyVoxelFiltered()` 执行自适应滤波

---

### **在SLAM中的意义**

该滤波器是Cartographer前端处理的关键步骤：

1. **降低计算负担**：减少后端优化中匹配的点数
2. **保持几何特征**：体素化后关键结构（如墙角、平面）仍可保留
3. **抗噪声**：蓄水池采样抑制局部噪声点的干扰
4. **可配置性**：通过Lua调节参数适应不同场景（室内/室外）
