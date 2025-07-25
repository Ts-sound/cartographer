# transform

[toc]


# timestamped_transform.h

* proto消息转换


# euler angles

* https://en.wikipedia.org/wiki/Euler_angles

> 在航空航天和机器人学中，物体的3D方向通常用三个角度来描述：roll（滚转角）、pitch（俯仰角）和yaw（偏航角）。这三个角度统称为欧拉角，它们描述了物体绕固定坐标系的三个轴的旋转。

1. ​​基本定义​​
​​Roll (滚转角)​​: 绕​​X轴​​旋转的角度。它表示物体绕前后轴的旋转（比如飞机的侧滚）。正角度表示逆时针旋转（从轴的负方向观察）。
​​Pitch (俯仰角)​​: 绕​​Y轴​​旋转的角度。它表示物体绕左右轴的旋转（比如飞机的俯仰）。正角度表示抬头（机头向上）。
​​Yaw (偏航角)​​: 绕​​Z轴​​旋转的角度。它表示物体绕垂直轴的旋转（比如飞机的偏航）。正角度表示逆时针旋转（从上往下看，飞机向左转）。

<figure style="text-align: center;">
  <img src="./assets/puml/transform/euler_aircraft.png" alt="描述" width="300">
  <figcaption style="text-align: center; font-style: italic;">图: roll-pitch-yaw </figcaption>
</figure>


2. ​​坐标系约定​​
通常使用​​右手坐标系​​：
​​X轴​​：指向物体的前方（或参考方向）
​​Y轴​​：指向物体的右侧
​​Z轴​​：指向物体的下方（航空航天中通常向上为正，但这里按照右手坐标系，Z轴向下是常见的）


<figure style="text-align: center;">
  <img src="./assets/puml/transform/Euler2a.gif" alt="描述" width="300">
  <figcaption style="text-align: center; font-style: italic;">图: example z-x′-z″ </figcaption>
</figure>

3. 在右手坐标系中：
大拇指指向 +X 轴方向。
食指指向 +Y 轴方向。
中指指向 +Z 轴方向。
绕一个坐标轴的正旋转方向由右手定则确定：弯曲右手四指指向旋转方向，则大拇指指向该轴的正方向。

---

# Quaternion （四元数）

表示形式​​:
​​代数形式​​：q=w+xi+yj+zk
​​标量-向量形式​​：q=(w,v)，其中 v=(x,y,z)是三维向量。
​​分量形式​​：q=[w,x,y,z]

---

# Axis–angle 
* 按指定轴向量进行角度旋转；

- example:
- **旋转描述**：当观察者站在地面（重力方向为负z轴），左转90度等同于绕z轴旋转 π/2 弧度（即90度）。
- **轴角表示法（Axis-Angle Representation）**：
  - 单位旋转轴向量：\(\begin{bmatrix} a_x \\ a_y \\ a_z \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix}\)（指向z轴正方向）。
  - 旋转角度：\(\theta = \frac{\pi}{2}\)。
  - 完整表示：\(\left\langle \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix}, \frac{\pi}{2} \right\rangle\)。
- **等价旋转向量表示（Rotation Vector）**：
  - 该向量定义为：\(\begin{bmatrix} 0 \\ 0 \\ \frac{\pi}{2} \end{bmatrix}\)，其中向量的模（大小）等于旋转角度 \(\frac{\pi}{2}\)，方向对应旋转轴 \([0, 0, 1]\)。
  
---

# Rotation

您提到的 "Rotation 表示" 在三维空间中通常有**两种标准表示法**，都与图片中的解释直接相关：

---

### 1. **轴角表示法 (Axis-Angle Representation)**  
   - **定义**：旋转 = **单位旋转轴向量** + **旋转角度**  
     - 轴向量：\(\mathbf{a} = \begin{bmatrix} a_x \\ a_y \\ a_z \end{bmatrix}\)（需满足 \(\|\mathbf{a}\| = 1\))  
     - 角度：\(\theta\)（弧度制）  
   - **示例**（图片中的左转90°）：  
     \[
     \mathbf{a} = \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix}, \quad \theta = \frac{\pi}{2}
     \]

---

### 2. **旋转向量表示法 (Rotation Vector)**  
   - **定义**：将轴角压缩为一个向量：\(\mathbf{v} = \theta \cdot \mathbf{a}\)  
     - 方向 = 旋转轴方向  
     - 模长 \(\|\mathbf{v}\| = \theta\) = 旋转角度  
   - **示例**：  
     \[
     \mathbf{v} = \theta \cdot \mathbf{a} = \frac{\pi}{2} \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \frac{\pi}{2} \end{bmatrix}
     \]

---

### 其他常见表示法的对比
| **表示法**          | **形式**                  | **特点**                     |
|---------------------|---------------------------|-----------------------------|
| 轴角表示法          | \(\langle \mathbf{a}, \theta \rangle\) | 直观，但需单位向量约束      |
| 旋转向量            | \(\mathbf{v} = \theta \mathbf{a}\)     | 紧凑，适合数值计算          |
| 旋转矩阵            | \(3 \times 3\) 正交矩阵     | 无奇异性，可复合旋转        |
| 四元数 (Quaternion) | \(q = [\cos(\theta/2), \, \mathbf{a}\sin(\theta/2)]\) | 计算高效，避免万向节死锁  |

> **关键公式**：旋转向量 → 旋转矩阵的转换（罗德里格斯公式）:  
> \[
> R = \mathbf{I} + \sin\theta \cdot [\mathbf{a}]_\times + (1-\cos\theta) \cdot [\mathbf{a}]_\times^2
> \]  
> 其中 \([\mathbf{a}]_\times\) 是轴向量的叉积矩阵。

如有具体场景需求（如代码实现或不同表示转换），请进一步说明！ 🙂