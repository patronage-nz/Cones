import os
import random
import time

LAT_TOP = -36.841454
LAT_BOTTOM = -36.852618
LON_LEFT = 174.755159
LON_RIGHT = 174.771960


def generate_coordinate_pair():
    """
    Generate a random coordinate pair (latitude, longitude) within the bounding box.
    """
    lat = random.uniform(LAT_BOTTOM, LAT_TOP)
    lon = random.uniform(LON_LEFT, LON_RIGHT)
    return lat, lon


def generate_random_time():
    return time.time() - (random.randrange(30, (24*360)))


def generate_random_ip():
    return '.'.join([str(random.randrange(10, 192)) for _ in range(4)])


def main(num_cones):
    # Create output directory
    output_dir = 'test_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    for cone_id in range(num_cones):
        lines: list[str] = []
        cur_file = os.path.join(output_dir, str(cone_id))
        # create between 1 and 3 random previous locations
        rand_history_count = random.randrange(1, 4)
        init_x, init_y = generate_coordinate_pair()
        lines.append('|'.join(str(i) for i in [init_x, init_y, generate_random_ip(), generate_random_time()]))
        for _ in range(rand_history_count):
            rand_x, rand_y = generate_coordinate_pair()
            lines.append('|'.join(str(j) for j in [rand_x, rand_y, generate_random_ip(), generate_random_time()]))
        final_x, final_y = generate_coordinate_pair()
        lines.append('|'.join(str(k) for k in [final_x, final_y, generate_random_ip(), generate_random_time()]))
        with open(cur_file, 'w') as conef:
            conef.write('\n'.join(lines))
    
    print(f"Generated {num_cones} cone data files in '{output_dir}' directory.")


if __name__ == '__main__':
    NUM_CONES: int = 100
    main(NUM_CONES)
