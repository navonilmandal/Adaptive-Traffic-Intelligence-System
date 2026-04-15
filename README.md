# 🚗 Adaptive Traffic Intelligence System (ATIS)

An intelligent traffic navigation system that combines **Perception, Optimization, and Path Planning** to simulate autonomous driving behavior in dynamic environments using SUMO.

---

## 🧠 Overview

This project implements a **hybrid AI system** for autonomous vehicle navigation, integrating:

* Real-time **Perception Module**
* **A*** path planning algorithm
* **Particle Swarm Optimization (PSO)** for adaptive decision-making
* Dynamic traffic-aware routing

The system simulates how an intelligent vehicle:

* Understands its surroundings
* Makes decisions in real time
* Optimizes routes based on traffic conditions

---

## ⚙️ System Architecture

Perception → Decision Making → Path Planning → Vehicle Control

---

## 🔍 Key Features

### 🚘 Perception Module

* Detects lane position and structure
* Identifies leading vehicles (obstacle detection)
* Measures traffic density

### 🧭 Intelligent Routing

* Uses **A*** algorithm for pathfinding
* Dynamic cost function based on:

  * Traffic density
  * Waiting time

### 🧠 Optimization (PSO)

* Learns optimal weights for routing
* Adapts to real-time traffic conditions
* Improves decision quality over static methods

### ⚡ Real-Time Decision Making

* Lane changing
* Obstacle avoidance
* Speed control
* Dynamic rerouting under congestion

### 🎨 Visualization

* Route highlighting
* Comparative path analysis (distance vs traffic vs optimized)

---

## 🧩 Technologies Used

* Python
* SUMO (Simulation of Urban Mobility)
* TraCI API
* A* Search Algorithm
* Particle Swarm Optimization (PSO)

---

## 📂 Project Structure

```
├── perception.py       # Environment sensing
├── decision.py         # Decision-making logic
├── pso.py              # Optimization engine
├── astar.py            # Path planning
├── utils.py            # Helper functions
├── main.py             # Simulation entry point
```

---

## 🚀 How It Works

1. **Perception Module**

   * Collects real-time data from SUMO using TraCI

2. **Optimization (PSO)**

   * Learns optimal weights for traffic-aware routing

3. **Path Planning (A*)**

   * Computes best route using dynamic cost function

4. **Decision Maker**

   * Executes driving logic:

     * Lane changes
     * Braking
     * Rerouting

---

## 🧠 Core Idea

Instead of using static shortest-path routing, this system dynamically optimizes routes using:

cost = distance × (1 + w1 × density + w2 × waiting_time)

Where:

* w1, w2 are learned using PSO

---

## 📊 Example Behaviors

* Avoids congested roads
* Changes lanes when obstacles are detected
* Re-routes dynamically during traffic spikes
* Demonstrates adaptive intelligence

---

## ⚠️ Limitations

* No future traffic prediction
* No reinforcement learning
* Uses simplified traffic metrics

---

## 🔮 Future Improvements

* Deep Learning-based perception (Computer Vision)
* Reinforcement Learning for decision-making
* Multi-agent coordination
* Predictive traffic modeling

---

## 🎯 Use Cases

* Autonomous driving research
* Traffic optimization systems
* AI-based simulation environments
* Academic projects and demonstrations

---

## 👨‍💻 Author

**Navonil Mandal**
CSE Student | AI & ML Enthusiast

---

## ⭐ If you like this project

Give it a star ⭐ and feel free to contribute!

---
