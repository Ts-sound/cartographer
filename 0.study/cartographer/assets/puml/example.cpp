#include <iostream>
#include <string>
#include <vector>
#include <memory>

// 1. 基础类：Vehicle
class Vehicle {
public:
    Vehicle(std::string name) : name(name) {}
    virtual void move() {
        std::cout << name << " is moving" << std::endl;
    }
private:
    std::string name;
};

// 2. 接口：Drivable
class Drivable {
public:
    virtual void drive() = 0;  // 纯虚函数定义接口
    virtual ~Drivable() = default;
};

// 3. Engine 部件类
class Engine {
public:
    Engine(std::string model) : model(model) {}
    void start() {
        std::cout << model << " engine started" << std::endl;
    }
private:
    std::string model;
};

// 4. Wheel 部件类
class Wheel {
public:
    Wheel(int size) : size(size) {}
    void rotate() {
        std::cout << size << "-inch wheel rotating" << std::endl;
    }
private:
    int size;
};

// 5. GPS 类
class GPS {
public:
    void locate() {
        std::cout << "Getting current position" << std::endl;
    }
};

// 6. Car 类 (继承 Vehicle 并包含其他组件)
class Car : public Vehicle, public Drivable {
public:
    // 构造函数 - 创建组合关系中的 Engine
    Car(std::string brand, std::string engineModel) 
        : Vehicle(brand), brand(brand), engine(engineModel) {}
    
    // 实现接口方法
    void drive() override {
        engine.start();
        std::cout << brand << " is driving" << std::endl;
    }
    
    // 弱依赖关系方法
    void navigate(GPS& gps) {  // 参数传递体现弱依赖
        gps.locate();
        std::cout << "Calculating route..." << std::endl;
    }
    
    // 聚合关系管理方法
    void addWheel(Wheel* w) {
        wheels.push_back(w);
    }
    
    void rotateWheels() {
        for (auto w : wheels) {
            w->rotate();
        }
    }
    
    ~Car() {
        for (auto w : wheels) {
            delete w;  // 清理资源
        }
    }

private:
    std::string brand;
    Engine engine;              // 构成关系 (Engine是Car的组成部分)
    std::vector<Wheel*> wheels; // 聚合关系 (Wheel对象独立存在)
};

// 7. Driver 类 (实现接口并依赖Car)
class Driver : public Drivable {
public:
    Driver(std::string name) : name(name) {}
    
    // 实现接口方法
    void drive() override {
        if (car) {
            car->drive();
            std::cout << name << " is driving the car" << std::endl;
        }
    }
    
    // 强依赖关系
    void assignCar(Car* c) {
        car = c;
    }
    
private:
    std::string name;
    Car* car;  // 强依赖关系 (Driver对象使用Car对象)
};

// 测试代码
int main() {
    // 创建独立部件
    Wheel* w1 = new Wheel(18);
    Wheel* w2 = new Wheel(18);
    Wheel* w3 = new Wheel(18);
    Wheel* w4 = new Wheel(18);
    
    // 创建汽车 (包含Engine构成关系)
    Car myCar("Toyota", "V6");
    
    // 添加轮胎 (聚合关系)
    myCar.addWheel(w1);
    myCar.addWheel(w2);
    myCar.addWheel(w3);
    myCar.addWheel(w4);
    
    // 创建驾驶员 (强依赖关系)
    Driver john("John");
    john.assignCar(&myCar);
    
    // 使用接口方法
    john.drive();
    
    // 弱依赖关系演示
    GPS navigator;
    myCar.navigate(navigator);
    
    return 0;
}

/*

1.继承 (Inheritance)​​
class Car : public Vehicle - Car 特化自 Vehicle
​2. ​接口实现 (Interface Implementation)​​
class Driver : public Drivable 和 class Car : public Drivable 并实现 drive() 纯虚函数
​
3.​构成关系 (Composition)​​
Engine engine; - Car 类直接包含 Engine 成员对象（Engine 生命周期与 Car 绑定）
​
4.​聚合关系 (Aggregation)​​
std::vector<Wheel*> wheels; - Car 保存 Wheel 指针集合（Wheel 对象独立创建和管理）
​
5.​强依赖 (Strong Dependency)​​
Car* car; - Driver 类持有 Car 对象的指针（直接关联使用）
​
6.​弱依赖 (Weak Dependency)​​
void navigate(GPS& gps) - Car 通过方法参数临时使用 GPS 对象（无持久关联）

*/