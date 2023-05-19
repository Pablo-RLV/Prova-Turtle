#!/usr/bin/env python3

import rclpy 
from rclpy.node import Node

from geometry_msgs.msg import Twist 
from turtlesim.msg import Pose
from collections import deque

import csv

# pontos_x = [0.0, 0.5, 0.0, 0.5, 0.0, 1.0]
# pontos_y = [0.5, 0.0, 0.5, 0.0, 1.0, 0.0]

class Pilha(deque):
    def __init__(self):
        super().__init__()

    def pilha_push(self, pose):
        super().append(pose)

    def pilha_pop(self):
        return super().pop()

class Fila(deque):
    def __init__(self):
        super().__init__()
        with open('pontos.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                new_pose = Pose_Turtle()
                new_pose.x, new_pose.y = [float(x) for x in row]
                self.fila_enqueue(new_pose)
        # for i in range(len(pontos_x)):
        #     new_pose = Pose_Turtle()
        #     new_pose.x = float(pontos_x[i])
        #     new_pose.y = float(pontos_y[i])
        #     self.fila_enqueue(new_pose)
        #     i += 1

    def fila_enqueue(self, pose):
        super().append(pose)

    def fila_dequeue(self):
        return super().popleft()
    
class Pose_Turtle(Pose):
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        super().__init__(x=x, y=y, theta=theta)
        self.limite = 0.1

    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __eq__(self, other):
        return abs(self.x - other.x) <= self.limite and abs(self.y - other.y) <= self.limite
    
class TurtleController(Node):
    def __init__(self, fila, pilha, control_period=0.02):
        super().__init__('tortuguita')
        self.limite = 0.1
        self.pose = Pose_Turtle(x=-40.0)
        self.set_point = Pose_Turtle(x=-40.0)
        self.fila = fila
        self.pilha = pilha
        self.publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(Pose, 'turtle1/pose', self.listener_callback, 10)
        self.control_timer = self.create_timer(timer_period_sec=control_period, callback=self.control_callback)

    def control_callback(self):
        if self.pose.x == -40.0:
            return
        msg = Twist()
        x_diff = self.set_point.x - self.pose.x
        y_diff = self.set_point.y - self.pose.y
        if self.pose == self.set_point:
            msg.linear.x = 0.0
            msg.linear.y = 0.0
            self.update_set_point()
        if abs(x_diff) > self.limite:
            if x_diff > 0:
                msg.linear.x = 0.25
            else:
                msg.linear.x = -0.25
        else:
            msg.linear.x = 0.0
        if abs(y_diff) > self.limite:
            if y_diff > 0:
                msg.linear.y = 0.25
            else:
                msg.linear.y = -0.25
        else:
            msg.linear.y = 0.0
        self.publisher.publish(msg)

    def update_set_point(self):
        try:
            self.set_point = self.fila.fila_dequeue() + self.pose
            self.pilha.pilha_push(self.set_point)
        except IndexError:
            self.get_logger().info('Fila vazia')
            try:
                self.set_point = self.pilha.pilha_pop()
            except IndexError:
                self.get_logger().info('Pilha vazia')
                exit()

    def listener_callback(self, msg):
        self.pose = Pose_Turtle(x=msg.x, y=msg.y, theta=msg.theta)
        if self.set_point.x == -40.0:
            self.update_set_point()

def main():
    rclpy.init()
    fila = Fila()
    pilha = Pilha()
    turtle_controller = TurtleController(fila, pilha)
    rclpy.spin(turtle_controller)
    turtle_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()