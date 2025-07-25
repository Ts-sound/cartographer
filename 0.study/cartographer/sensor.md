# transform

[toc]

感知数据定义(PointCloud,Imu,Odometry)

# 数据类型定义 及 Proto转换

- **point_cloud.h** PointCloud ： 点云数据
- **odometry_data.h** OdometryData ： 里程计数据
- **imu_data.h** ImuData ： 陀螺仪数据
- **fixed_frame_pose_data.h** FixedFramePoseData ： 固定帧位姿数据。用于存储类似于GPS或固定位置的数据，这些数据将在优化过程中使用。
- 
- **timed_point_cloud_data.h** TimedPointCloudData ： ？
- **range_data.h** RangeData ： ？
- **map_by_time.h** MapByTime ： ？
- **landmark_data.h** LandmarkData ： ？

rangefinder,测距仪,

# data.h

![](./assets/puml/sensor/data.puml)

```c++
/// cartographer/sensor/internal/dispatchable.h
/// 用unique_ptr 创建一个可被分派的数据对象(ImuData,PointcloudData,...)
template <typename DataType>
std::unique_ptr<Dispatchable<DataType>> MakeDispatchable(
    const std::string &sensor_id, const DataType &data) {
  return absl::make_unique<Dispatchable<DataType>>(sensor_id, data);
}
```

# compressed_point_cloud.h

* CompressedPointCloud 点云压缩类;
  * 目的：压缩ponits以减少存储空间, 有精度损失;
  * 精度定义: constexpr float kPrecision = 0.001f;  // in meters.