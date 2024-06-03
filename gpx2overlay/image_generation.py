import os
from PIL import Image, ImageDraw
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def generate_image(index, row, base_image, output_dir, img_size):
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    x = row['normalized_longitude'] * img_size[0]
    y = img_size[1] - row['normalized_latitude'] * img_size[1]
    draw.ellipse([x-5, y-5, x+5, y+5], fill="orange")

    img.save(os.path.join(output_dir, f'frame_{index+1:04d}.png'))

def create_images(points_df, output_dir, img_size):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    route_image = Image.new('RGBA', img_size, (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route_image)
    for i in range(1, len(points_df)):
        route_draw.line(
            [
                (points_df['normalized_longitude'].iloc[i-1] * img_size[0],
                img_size[1] - points_df['normalized_latitude'].iloc[i-1] * img_size[1]),
                (points_df['normalized_longitude'].iloc[i] * img_size[0],
                img_size[1] - points_df['normalized_latitude'].iloc[i] * img_size[1])
            ],
            fill="white",
            width=3
        )

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_image, index, row, route_image, output_dir, img_size)
            for index, row in points_df.iterrows()
        ]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating images"):
            future.result()

    print(f'Images saved in directory: {output_dir}')
