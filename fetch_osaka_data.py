import os
import osmnx as ox
import geopandas as gpd

def fetch_and_save_map_data(place_name, output_dir):
    print(f"Đang tải dữ liệu đồ thị đường phố cho: {place_name}...")
    # Có thể thêm tham số simplify=True để giảm bớt các node không phải giao lộ
    G = ox.graph_from_place(place_name, network_type='drive')
    
    print("Đang chuyển đổi đồ thị thành DataFrames...")
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    
    map_dir = os.path.join(output_dir, 'map')
    os.makedirs(map_dir, exist_ok=True)
    
    # Reset index để đưa osmid, u, v, key thành các cột bình thường
    df_nodes = gdf_nodes.reset_index()
    df_edges = gdf_edges.reset_index()
    
    # ---------------------------------------------------------
    # 1. FIX LỖI LIST VÀ CHUẨN BỊ DATA
    # ---------------------------------------------------------
    print("Đang dọn dẹp dữ liệu (xử lý các cột dạng list)...")
    
    # Xử lý edges: Bỏ qua cột 'geometry' để tránh lỗi AttributeError
    for col in df_edges.columns:
        if col != 'geometry' and df_edges[col].map(lambda x: isinstance(x, list)).any():
            df_edges[col] = df_edges[col].astype(str)
            
    # Làm tương tự cho nodes để đề phòng an toàn
    for col in df_nodes.columns:
        if col != 'geometry' and df_nodes[col].map(lambda x: isinstance(x, list)).any():
            df_nodes[col] = df_nodes[col].astype(str)

    # ---------------------------------------------------------
    # 2. LỌC CỘT THEO ĐÚNG YÊU CẦU & LƯU CSV
    # ---------------------------------------------------------
    print("Đang định dạng cột và lưu nodes.csv, edges.csv...")
    
    desired_node_cols = ["osmid", "y", "x", "street_count", "highway", "geometry"]
    desired_edge_cols = ["u", "v", "key", "osmid", "oneway", "name", "highway", "reversed", "length", "lanes", "geometry", "service", "access"]
    
    # Dùng reindex để ép khung DataFrame theo đúng các cột mong muốn
    df_nodes_csv = df_nodes.reindex(columns=desired_node_cols)
    df_edges_csv = df_edges.reindex(columns=desired_edge_cols)
    
    df_nodes_csv.to_csv(os.path.join(output_dir, 'nodes.csv'), index=False)
    df_edges_csv.to_csv(os.path.join(output_dir, 'edges.csv'), index=False)
    
    # ---------------------------------------------------------
    # 3. LƯU FILE GEOJSON VÀO FOLDER 'map'
    # ---------------------------------------------------------
    print("Đang lưu các file .geojson...")
    # Lấy lại định dạng GeoDataFrame để lưu GeoJSON hợp lệ
    gdf_nodes_clean = gpd.GeoDataFrame(df_nodes, geometry='geometry')
    gdf_edges_clean = gpd.GeoDataFrame(df_edges, geometry='geometry')
    
    try:
        boundary = ox.geocode_to_gdf(place_name)
        boundary.to_file(os.path.join(map_dir, 'osaka_boundary.geojson'), driver="GeoJSON")
    except Exception as e:
        print(f"Không thể lấy ranh giới: {e}")

    gdf_nodes_clean.to_file(os.path.join(map_dir, 'nodes.geojson'), driver="GeoJSON")
    gdf_edges_clean.to_file(os.path.join(map_dir, 'edges.geojson'), driver="GeoJSON")
    
    print("Hoàn tất xuất dữ liệu!")

if __name__ == "__main__":
    TARGET_DIR = "./data" 
    PLACE = "Kita, Osaka, Japan" 
    fetch_and_save_map_data(PLACE, TARGET_DIR)