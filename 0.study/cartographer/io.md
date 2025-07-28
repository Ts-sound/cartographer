# io

* 从文件中反序列化（读取）Proto协议数据的工具
  * all_trajectory_builder_options : 存储所有轨迹的配置参数
  * pose_graph : 位姿图
* 保存地图数据（pbstream）
* 使用cairo画图（未见使用）

[toc]

## ProtoStreamDeserializer

> 反序列化（读取）Proto协议数据的工具

* all_trajectory_builder_options : 存储所有轨迹的配置参数
* pose_graph : 位姿图

![PointsProcessor](./assets/puml/io/rw.puml)

![ProtoStreamDeserializer_call](./assets/puml/io/ProtoStreamDeserializer_call.png)

## mapping_state_serialization.h

```c++

// The current serialization format version.
static constexpr int kMappingStateSerializationFormatVersion = 2;
static constexpr int kFormatVersionWithoutSubmapHistograms = 1;

// Serialize mapping state to a pbstream.
void WritePbStream(
    const mapping::PoseGraph& pose_graph,
    const std::vector<mapping::proto::TrajectoryBuilderOptionsWithSensorIds>&
        builder_options,
    ProtoStreamWriterInterface* const writer, bool include_unfinished_submaps);

```

 `WritePbStream` 函数:
将 SLAM 构建的地图状态（包括位姿图、子图、传感器数据等）序列化为 Protobuf 格式的二进制流。

---

### **关键数据结构**

* 轨迹状态 (`trajectory_states`)
* 子图集合 (`submap_data`)
* 轨迹节点 (`trajectory_nodes`)
* 传感器数据（IMU、里程计等）
* 地标节点 (`landmark_nodes`)

* **`SerializedData`**: 序列化数据的容器，通过 Protobuf 消息封装不同类型的数据。

---

### **核心函数：`WritePbStream`**

**执行流程**：

1. **写入文件头**
   * 调用 `CreateHeader()` 生成包含版本信息的头部。

2. **序列化位姿图**
   * `SerializePoseGraph()`: 将位姿图转换为 Protobuf 格式，通过 `include_unfinished_submaps` 控制是否包含未完成的子图。

3. **序列化轨迹配置**
   * `SerializeTrajectoryBuilderOptions()`: 将各轨迹的构建选项（传感器配置、算法参数等）序列化，仅包含状态非 `DELETED` 的轨迹（通过 `GetValidTrajectoryIds` 过滤）。

4. **序列化具体数据**
   * **子图 (`SerializeSubmaps`)**  
     遍历所有子图，跳过未完成的子图（如果 `include_unfinished_submaps=false`），将子图栅格数据及其 ID 序列化。
   * **轨迹节点 (`SerializeTrajectoryNodes`)**  
     将所有节点（位置、传感器帧）转换为 Protobuf。
   * **轨迹物理数据 (`SerializeTrajectoryData`)**  
     包含重力常数、IMU 校准参数、坐标系变换。
   * **传感器数据**:
     * `SerializeImuData()`: 序列化所有轨迹的 IMU 测量值。
     * `SerializeOdometryData()`: 序列化里程计数据。
     * `SerializeFixedFramePoseData()`: 序列化固定坐标系位姿。
   * **地标数据 (`SerializeLandmarkNodes`)**  
     将地标节点及其观测信息（时间戳、位姿变换、权重）序列化。

---

### **技术细节**

1. **数据过滤机制**
   * `GetValidTrajectoryIds`: 过滤已删除的轨迹，确保仅序列化有效数据。
   * `include_unfinished_submaps`: 控制是否包含未优化完成的子图。

2. **ID 映射处理**
   * 子图 (`SubmapId`)、节点 (`NodeId`) 等均通过 `(trajectory_id, index)` 二元组唯一标识，并在序列化时显式存储。

3. **传感器数据处理**
   * 使用 `MapByTime` 模板按时间戳组织传感器数据，保证时序正确性。
   * 地标节点观测信息包含权重（`translation_weight` 和 `rotation_weight`），用于后续优化。

4. **坐标系变换**
   * `transform::ToProto`: 将 Eigen 矩阵转换为 Protobuf 格式（如 `fixed_frame_origin_in_map`）。

---

### **使用场景**

该序列化功能用于：

1. **地图保存与加载**: 将构建的地图持久化存储。
2. **回环检测与优化**: 存储中间状态以支持分布式处理。
3. **算法调试**: 导出完整数据用于离线分析。

通过此实现，Cartographer 可确保地图状态的高效、完整序列化，为 SLAM 系统的实际部署提供基础支持。

## PointsProcessor

> 使用cairo画图,cartographer内部未见使用该功能；

![PointsProcessor](./assets/puml/io/image_processor.puml)

![Alt text](./assets/puml/io/PointsProcessorPipelineBuilder_find.png)

## cairo

* Cairo（libcairo）​​ 是一个开源的 ​​2D 矢量图形库​​，用于图形输出(PNG,SVG,PCD,...)
* link : <https://www.cairographics.org/>
