from PIL import Image, ImageFilter, ImageOps


def apply_grayscale(image: Image.Image) -> Image.Image:
    return ImageOps.grayscale(image)


def apply_blur(image: Image.Image) -> Image.Image:
    return image.filter(ImageFilter.GaussianBlur(radius=2))


def apply_edges(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    return gray.filter(ImageFilter.FIND_EDGES)


def apply_binary(image: Image.Image, threshold: int = 128) -> Image.Image:
    gray = ImageOps.grayscale(image)
    return gray.point(lambda pixel: 255 if pixel > threshold else 0)


def apply_sharpen(image: Image.Image) -> Image.Image:
    return image.filter(ImageFilter.SHARPEN)


def apply_invert(image: Image.Image) -> Image.Image:
    rgb_image = image.convert("RGB")
    return ImageOps.invert(rgb_image)
