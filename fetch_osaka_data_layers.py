import os
import osmnx as ox

def fetch_geojson_layers_by_radius(center_point, radius, output_dir, place_name_for_log):
    map_dir = os.path.join(output_dir, 'map')
    os.makedirs(map_dir, exist_ok=True)

    print(f"Bắt đầu tải các lớp bản đồ GeoJSON cho khu vực {place_name_for_log}")
    print(f"Tâm: {center_point}, Bán kính: {radius} mét...")

    geojson_queries = {
        "buildings": {"building": True},
        "roads": {"highway": True},
        "water_areas": {"natural": ["water", "bay"], "water": True, "waterway": ["riverbank"]},
        "water_lines": {"waterway": ["river", "stream", "canal", "ditch"]},
        "forests": {"landuse": ["forest"], "natural": ["wood"]},
        "railways": {"railway": True},
        "amenity_points": {"amenity": True},
        "bridges": {"bridge": True},
        "tunnels": {"tunnel": "yes"},
        "landcover": {"landuse": ["grass", "meadow", "orchard"], "natural": ["scrub", "heath"]},
    }

    for filename, tags in geojson_queries.items():
        print(f"Đang tải dữ liệu cho {filename}.geojson...")
        try:
            # Dùng features_from_point thay vì features_from_place
            try:
                gdf = ox.features_from_point(center_point, tags, dist=radius)
            except AttributeError:
                # Dành cho các bản osmnx cũ hơn
                gdf = ox.geometries_from_point(center_point, tags, dist=radius)

            if not gdf.empty:
                # Ép kiểu dữ liệu list/dict thành string để tránh lỗi
                for col in gdf.columns:
                    if col != 'geometry':
                        gdf[col] = gdf[col].astype(str)

                file_path = os.path.join(map_dir, f"{filename}.geojson")
                gdf.to_file(file_path, driver="GeoJSON")
                print(f"  -> Thành công: Đã lưu {filename}.geojson (Số lượng: {len(gdf)})")
            else:
                print(f"  -> Trống: Không tìm thấy đối tượng nào cho {filename}")
                
        except Exception as e:
            print(f"  -> Lỗi khi tải {filename}: {e}")

    print("\nHoàn tất tải các file GeoJSON!")

if __name__ == "__main__":
    TARGET_DIR = "./data"
    
    # --- CẤU HÌNH TỌA ĐỘ TRUNG TÂM VÀ BÁN KÍNH ---
    
    # Lựa chọn 1: Trung tâm Dotonbori (Khu phố sầm uất ven sông)
    CENTER_COORDS = (34.6687, 135.5013) # (Vĩ độ - Latitude, Kinh độ - Longitude)
    LOCATION_NAME = "Dotonbori"
    
    # Lựa chọn 2: Trung tâm Namba (Ga tàu lớn, nhiều đường giao nhau)
    # Nếu muốn dùng Namba, bỏ comment 2 dòng dưới và comment 2 dòng trên
    # CENTER_COORDS = (34.6630, 135.5015) 
    # LOCATION_NAME = "Namba"
    
    # Bán kính tải dữ liệu (tính bằng mét). 
    # 800m - 1000m là lý tưởng để file dưới 1MB và hiển thị cực nhanh trên Github
    RADIUS_METERS = 800 
    
    fetch_geojson_layers_by_radius(CENTER_COORDS, RADIUS_METERS, TARGET_DIR, LOCATION_NAME)