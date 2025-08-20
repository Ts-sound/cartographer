# 
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patheffects as path_effects

def gravity_align_points(points, sensor_orientation):
    """重力对齐点云"""
    # 传感器原始Z轴
    sensor_z = sensor_orientation[:, 2]
    gravity_vector = np.array([0, 0, -1])  # 重力方向
    
    # 计算旋转矩阵
    v = np.cross(sensor_z, gravity_vector)
    c = np.dot(sensor_z, gravity_vector)
    s = np.linalg.norm(v)
    if s < 1e-6:
        return points, np.eye(3)
    
    kmat = np.array([[0, -v[2], v[1]], 
                     [v[2], 0, -v[0]], 
                     [-v[1], v[0], 0]])
    
    R = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return np.dot(points, R.T), R

def visualize_point_transformation(original_points, aligned_points, sensor_orientation, R):
    """可视化4个关键点的变换过程"""
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle("重力对齐过程：4个关键点的位置变化", fontsize=16)
    
    # 创建两个子图
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')
    
    # 原始点云（传感器坐标系）
    ax1.set_title("原始传感器坐标系")
    ax2.set_title("重力对齐坐标系")
    
    # 共同设置
    for ax in [ax1, ax2]:
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.view_init(elev=30, azim=45)
        
    # 在原始坐标系中绘制点和坐标轴
    colors = ['r', 'g', 'b', 'm']
    labels = ['传感器原点 (0,0,0)', 
             '前方向 (1,0,0)', 
             '左方向 (0,1,0)', 
             '上方向 (0,0,1)']
    
    # 原始传感器坐标系中的点
    for i, point in enumerate(original_points):
        ax1.scatter(*point, s=100, color=colors[i], alpha=0.9)
        
        # 在点旁添加标签
        text = ax1.text(*point, labels[i], fontsize=9)
        text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='w')])
    
    # 绘制原始坐标轴
    origin = original_points[0]
    axis_labels = ['X (前)', 'Y (左)', 'Z (上)']
    for i in range(3):
        axis_point = np.zeros(3)
        axis_point[i] = 1.0
        direction = np.dot(axis_point, sensor_orientation.T)
        ax1.quiver(*origin, *direction, color=colors[i+1], length=0.8, 
                  arrow_length_ratio=0.1, linewidth=2, alpha=0.7)
        ax1.text(*(origin + direction*0.9), axis_labels[i], color=colors[i+1], fontsize=10)
    
    # 在重力对齐坐标系中绘制点和坐标轴
    for i, point in enumerate(aligned_points):
        ax2.scatter(*point, s=100, color=colors[i], alpha=0.9)
        text = ax2.text(*point, labels[i], fontsize=9)
        text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='w')])
        
        # 绘制变换轨迹
        ax2.plot([original_points[i][0], point[0]], 
                 [original_points[i][1], point[1]], 
                 [original_points[i][2], point[2]], 
                 'k--', alpha=0.5)
    
    # 绘制重力对齐坐标轴
    gravity_direction = np.array([0, 0, -1])
    ax2.quiver(*aligned_points[0], *[0.8, 0, 0], color='r', length=0.8, 
              arrow_length_ratio=0.1, linewidth=2, alpha=0.7)
    ax2.text(*aligned_points[0] + [0.75, 0, 0], "X (水平方向)", color='r', fontsize=10)
    
    ax2.quiver(*aligned_points[0], *[0, 0.8, 0], color='g', length=0.8, 
              arrow_length_ratio=0.1, linewidth=2, alpha=0.7)
    ax2.text(*aligned_points[0] + [0, 0.8, 0], "Y (水平方向)", color='g', fontsize=10)
    
    ax2.quiver(*aligned_points[0], *[0, 0, -0.8], color='b', length=0.8, 
              arrow_length_ratio=0.1, linewidth=2, alpha=0.7)
    ax2.text(*aligned_points[0] + [0, 0, -0.9], "Z (重力方向)", color='b', fontsize=10)
    
    # 在右侧图中添加重力方向标注
    ax2.text(0, 0, -1.1, "重力方向", color='k', ha='center')
    ax2.quiver(0, 0, -1, 0, 0, -0.1, color='k', arrow_length_ratio=0.2, linewidth=2)
    
    # 添加转换矩阵信息
    matrix_text = f"旋转矩阵 R:\n" + "\n".join(
        ["  ".join([f"{val:.3f}" for val in row]) for row in R]
    )
    fig.text(0.5, 0.05, matrix_text, ha='center', fontsize=12, bbox=dict(facecolor='whitesmoke', alpha=0.8))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    # plt.savefig('gravity_alignment_4_points.png', dpi=120)
    plt.show()

def main():
    # 1. 创建4个关键点 (传感器坐标系)
    points = np.array([
        [0, 0, 0],  # 传感器原点
        [1, 0, 0],  # 传感器正前方 (X)
        [0, 1, 0],  # 传感器左侧 (Y)
        [0, 0, 1]   # 传感器正上方 (Z)
    ])
    
    # 2. 创建传感器倾斜方向 (横滚10度，俯仰5度)
    roll = np.radians(10)  # 横滚角
    pitch = np.radians(5)  # 俯仰角
    
    R_roll = np.array([[1, 0, 0],
                       [0, np.cos(roll), -np.sin(roll)],
                       [0, np.sin(roll), np.cos(roll)]])
    
    R_pitch = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                        [0, 1, 0],
                        [-np.sin(pitch), 0, np.cos(pitch)]])
    
    sensor_orientation = R_roll @ R_pitch
    
    # 3. 应用传感器方向到点
    oriented_points = points @ sensor_orientation.T
    
    # 4. 进行重力对齐
    aligned_points, R = gravity_align_points(oriented_points, sensor_orientation)
    
    # 5. 打印点和矩阵
    print("传感器原始点 (传感器坐标系):")
    for i, label in enumerate(["原点", "前方向", "左方向", "上方向"]):
        print(f"{label}: {oriented_points[i]}")
    
    print("\n重力对齐后的点 (重力坐标系):")
    for i, label in enumerate(["原点", "前方向", "左方向", "上方向"]):
        print(f"{label}: {aligned_points[i]}")
    
    print(f"\n旋转矩阵:\n{R}")
    
    # 6. 可视化
    visualize_point_transformation(oriented_points, aligned_points, sensor_orientation, R)

if __name__ == "__main__":
    main()