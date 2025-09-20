# HoloLens Computer Vision Samples

This directory contains Python tools for processing and analyzing HoloLens 2 mixed reality data streams.

## Overview

A comprehensive suite of tools for converting, processing, and analyzing data captured from HoloLens 2 devices, particularly focused on research and computer vision applications.

## Key Files

### Data Processing
- `convert_images.py` - Image format conversion and preprocessing utilities
- `process_all.py` - Batch processing pipeline for multiple data streams
- `recorder_console.py` - Console interface for HoloLens data recording

### Computer Vision Tools
- `project_hand_eye_to_pv.py` - Hand-eye coordination data projection to RGB camera
- `save_pclouds.py` - Point cloud extraction and saving utilities
- `utils.py` - Common utilities and helper functions

### 3D Processing
- `tsdf-integration.py` - Truncated Signed Distance Function integration for 3D reconstruction
- `hand_defs.py` - Hand tracking data definitions and processing

## Features

### Mixed Reality Data Processing
- Multi-stream data synchronization and alignment
- Real-time sensor data processing
- Spatial mapping and 3D reconstruction
- Hand tracking and gesture recognition

### Computer Vision Pipeline
- RGB-D image processing and analysis
- Point cloud generation and manipulation
- Coordinate system transformations
- Depth data processing and visualization

### Research Tools
- Data export and format conversion
- Batch processing capabilities
- Performance analysis and optimization
- Integration with research workflows

## Technology Stack

- **Computer Vision**: OpenCV, NumPy, point cloud processing
- **3D Processing**: TSDF integration, spatial mapping
- **HoloLens Integration**: Research mode data access
- **Data Processing**: Multi-format support, batch operations

## Applications

- Mixed reality research and development
- Computer vision algorithm testing
- 3D reconstruction and mapping
- Hand tracking and gesture analysis
- Spatial computing applications

## Development Context

These tools are designed for researchers and developers working with HoloLens 2 devices in computer vision and mixed reality applications. They provide essential functionality for processing and analyzing the rich sensor data available from the device.

## Usage

Each tool is designed for specific aspects of HoloLens data processing. Use in conjunction with HoloLens 2 research mode applications for comprehensive mixed reality development workflows.