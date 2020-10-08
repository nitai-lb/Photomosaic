############################
# FILE: photomosaic.py
# DESCRIPTION: A program that construct a mosaic.
############################
import copy
import mosaic
import sys
RED = 0
GREEN = 1
BLUE = 2
UNREACHABLE_DISTANCE = 257*3
NUMBER_OF_ARGUMENTS = 5


def compare_pixel(pixel1, pixel2):
    """
    the function compare 2 given pixels' colors by calculating the distance
    between each integer they made of and return the sum of the distances.
    :param pixel1: a tuple of 3 integers correspond to RGB colors.
    :param pixel2: a tuple of 3 integers correspond to RGB colors.
    :return: integer.
    """
    r = abs(pixel1[RED] - pixel2[RED])
    g = abs(pixel1[GREEN] - pixel2[GREEN])
    b = abs(pixel1[BLUE] - pixel2[BLUE])
    return r + g + b


def compare(image1, image2):
    """
    the function calculating distance between two images by summing the
    distance between each pixel.
    :param image1: list of lists containing RGB tuple.
    :param image2: list of lists containing RGB tuple.
    :return: distance between images.
    """
    dist = 0
    for r in range(min(len(image1), len(image2))):  # min rows out of the two
        # images.
        for c in range(min(len(image1[0]), len(image2[0]))):  # min columns
            # out of the two images.
            dist += compare_pixel(image1[r][c], image2[r][c])
    return dist


def get_piece(image, upper_left, size):
    """
    the function slicing a piece from image starting from the upper left corner
    according to the given size.
    :param image: list of lists containing RGB tuple.
    :param upper_left: tuple with coordinates of row and column.
    :param size: tuple of how many rows and columns.
    :return: a list of lists containing RGB tuple.
    """
    r, c = upper_left
    hgt, wid = size
    end_r, end_c = len(image), len(image[0])
    piece = [image[i][c:min(c + wid, end_c)] for i in range(r, min(r + hgt,
                                                                    end_r))]
    # the upper line copy the piece by slicing it out.
    return piece


def set_piece(image, upper_left, piece):
    """
    the function setting a piece into the image starting from a given upper
    left corner.
    :param image: list of lists containing RGB tuple.
    :param upper_left: tuple with coordinates of row and column.
    :param piece: list of lists containing RGB tuple.
    """
    r, c = upper_left  # coordinates in the image where the piece should be
    # putted.
    p_r, p_c = len(piece), len(piece[0])
    rows_image, cols_image = len(image), len(image[0])
    for row in range(r, min(p_r + r, rows_image)):
        for col in range(c, min(p_c + c, cols_image)):
            image[row][col] = piece[row - r][col - c]


def average(image):
    """
    the function summing the red, green and blue factors of each pixel and
    and return them divided by a number of pixels as a tuple.
    :param image: list of lists containing RGB tuple.
    :return: a tuple of RGB.
    """
    red, green, blue = 0, 0, 0
    rows = len(image)
    columns = len(image[0])
    pixels = rows * columns
    for row in range(rows):
        for column in range(columns):
            red += image[row][column][RED]
            green += image[row][column][GREEN]
            blue += image[row][column][BLUE]
    rgb = [red, green, blue]
    rgb = tuple(x/pixels for x in rgb)
    return rgb


def preprocess_tiles(tiles):
    """
    the function building a list of calculated averages for given tiles.
    :param tiles: a list of lists of lists containing RGB tuple.
    :return: a list of averages RGB for each tile.
    """
    tiles_avg = [average(tile) for tile in tiles]
    return tiles_avg


def get_best_tiles(objective, tiles, averages, num_candidates):
    """
    the function returning a list of tile that are the most closest to the
    objective average.
    :param objective: a list of lists containing RGB tuple.
    :param tiles: a list of lists of lists containing RGB tuple.
    :param averages: list of averages corresponding to tiles list.
    :param num_candidates: a number indicates how many should be returned.
    :return: list of the closest tiles to objective.
    """
    avg_obj = average(objective)
    best = []
    dist_lst = [compare_pixel(averages[tile], avg_obj) for tile in
                range(len(tiles))]
    while len(best) < num_candidates:
        best.append(tiles[dist_lst.index(min(dist_lst))])  # index of the
        # smallest distance.
        dist_lst[dist_lst.index(min(dist_lst))] = UNREACHABLE_DISTANCE
    return best


def choose_tile(piece, tiles):
    """
    the function returning the best tile out of a given tiles list according to
    distance between the pixels of both tile and piece.
    :param piece: a list of lists containing RGB tuple.
    :param tiles: a list of lists of lists containing RGB tuple.
    :return: RGB tuple.
    """
    dist_lst = [compare(tile, piece) for tile in tiles]
    the_best = tiles[dist_lst.index(min(dist_lst))]
    return the_best


def make_mosaic(image, tiles, num_candidates):
    """
    the function constructing a mosaic of tiles according to image.
    :param image: a list of lists containing RGB tuple.
    :param tiles: list of images.
    :param num_candidates: a number.
    :return: constructed mosaic made of tiles according to image.
    """
    tiles_avg_lst = [average(tile) for tile in tiles]
    height, width = len(tiles[0]), len(tiles[0][0])
    size = (height, width)
    row = 0  # index for rows.
    new_image = copy.deepcopy(image)
    while row < len(image):
        col = 0  # index for columns.
        while col < len(image[row]):
            col, new_image = piece_by_piece(new_image, row, col, tiles, size,
                                            width, tiles_avg_lst,
                                            num_candidates)
        row += height
    return new_image


def piece_by_piece(new_image, row, col, tiles, size, width, tiles_avg,
                   candidates):
    """
    the function setting the best tile from tiles instead of a piece in a
    chosen place and return the result. best tile is chosen from filtered
    tiles list.
    """
    upper = (row, col)
    piece = get_piece(new_image, upper, size)
    top_tiles = get_best_tiles(piece, tiles, tiles_avg, candidates)
    best_tile = choose_tile(piece, top_tiles)
    set_piece(new_image, upper, best_tile)
    col += width
    return col, new_image


if __name__ == '__main__':
    if len(sys.argv) == NUMBER_OF_ARGUMENTS + 1:
        script_name = sys.argv[0]
        image_source = sys.argv[1]
        images_dir = sys.argv[2]
        output_name = sys.argv[3]
        tile_height = int(sys.argv[4])
        num_candidates = int(sys.argv[5])
        tiles_list = mosaic.build_tile_base(images_dir, tile_height)
        the_image = mosaic.load_image(image_source)
        generated_image = make_mosaic(the_image, tiles_list, num_candidates)
        mosaic.save(generated_image, output_name)

    else:
        print('Wrong number of parameters. The correct usage is:\nphotomosaic.py '
              '<image_source> <images_dir> <output_name> <tile_height>'
              ' <num_candidates>')
