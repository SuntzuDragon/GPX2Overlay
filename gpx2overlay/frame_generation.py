import os
from PIL import Image, ImageDraw
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_route_image(points_df, img_size, fill_color, line_width):
    route_image = Image.new('RGBA', img_size, (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route_image)

    scaled_lons = points_df['norm_lon'] * img_size[0]
    scaled_lats = img_size[1] - points_df['norm_lat'] * img_size[1]

    point_rad = line_width // 2

    for i in range(1, len(points_df)):
        route_draw.line(
            [
                (scaled_lons.iloc[i-1], scaled_lats.iloc[i-1]),
                (scaled_lons.iloc[i], scaled_lats.iloc[i])
            ],
            fill=fill_color,
            width=line_width
        )

        route_draw.ellipse(
            [
                (scaled_lons.iloc[i] - point_rad,
                 scaled_lats.iloc[i] - point_rad),
                (scaled_lons.iloc[i] + point_rad,
                 scaled_lats.iloc[i] + point_rad)
            ],
            fill=fill_color,
            outline=fill_color)

    return route_image


def generate_frame(index, row, base_image, output_dir, img_size, point_rad):
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    x = row['norm_lon'] * img_size[0]
    y = img_size[1] - row['norm_lat'] * img_size[1]
    draw.ellipse([x-point_rad, y-point_rad, x +
                 point_rad, y+point_rad], fill="orange")

    img.save(os.path.join(output_dir, f'frame_{index+1:04d}.png'))


def create_frames(points_df, output_dir, img_size):
    os.makedirs(output_dir, exist_ok=True)

    route_image = generate_route_image(points_df, img_size, "white", 5)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_frame, index, row,
                            route_image, output_dir, img_size, 5)
            for index, row in points_df.iterrows()
        ]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating images"):
            future.result()

    print(f'Images saved in directory: {output_dir}')
