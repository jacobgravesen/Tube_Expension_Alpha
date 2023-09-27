import pyrealsense2 as rs

# Create a pipeline
pipeline = rs.pipeline()

# Start streaming
pipeline.start()

# Get the intrinsic parameters
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

print("Width:", intrinsics.width)
print("Height:", intrinsics.height)
print("PPX (cx):", intrinsics.ppx)
print("PPY (cy):", intrinsics.ppy)
print("FX:", intrinsics.fx)
print("FY:", intrinsics.fy)
print("Distortion:", intrinsics.model, intrinsics.coeffs)

# Stop streaming
pipeline.stop()