import csv
from sklearn.cluster import DBSCAN

def cluster_points_by_z(points_3d, eps=10, min_samples=1):
    # Extract the Z values from the points
    z_values = [[point[2]] for point in points_3d]

    # Apply the DBSCAN algorithm
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(z_values)

    # Create a dictionary where the keys are the cluster labels and the values are the points in each cluster
    clusters = {}
    for point, label in zip(points_3d, db.labels_):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(point)

    return clusters

def read_points_from_csv(file_path):
    points_3d = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header
        for row in reader:
            points_3d.append(list(map(float, row)))
    return points_3d

def main():
    file_path = 'robot_movement/required_points.csv'
    points_3d = read_points_from_csv(file_path)
    clusters = cluster_points_by_z(points_3d)

    # Calculate the average Z value for each cluster
    avg_z_values = {label: sum(point[2] for point in points) / len(points) for label, points in clusters.items()}

    # Sort the clusters based on the average Z values, in descending order
    sorted_clusters = sorted(clusters.items(), key=lambda item: avg_z_values[item[0]], reverse=True)

    for label, points in sorted_clusters:
        # Sort the points in the cluster based on their Y values, from lowest to highest
        sorted_points = sorted(points, key=lambda point: point[1])
        print(f"Cluster {label}: {len(sorted_points)} points, Average Z: {avg_z_values[label]}")
        for point in sorted_points:
            print(point)

if __name__ == "__main__":
    main()