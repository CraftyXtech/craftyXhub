const MAX_FILE_SIZE = 5 * 1024 * 1024;
const MIN_WIDTH = 1200;
const MIN_HEIGHT = 630;
const TARGET_RATIO = 1200 / 630;
const RATIO_TOLERANCE = 0.12;

export const FEATURED_IMAGE_GUIDANCE =
  'Use a clean 1200x630 landscape image. Avoid logos, watermarks, and text overlays.';

function readImageDimensions(file) {
  return new Promise((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file);
    const image = new Image();

    image.onload = () => {
      resolve({ width: image.width, height: image.height });
      URL.revokeObjectURL(objectUrl);
    };

    image.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      reject(new Error('Failed to read image dimensions.'));
    };

    image.src = objectUrl;
  });
}

export async function validateFeaturedImageFile(file) {
  if (!file) {
    return { ok: false, message: 'Please select an image file.' };
  }

  if (!file.type.startsWith('image/')) {
    return { ok: false, message: 'Please select an image file.' };
  }

  if (file.size > MAX_FILE_SIZE) {
    return { ok: false, message: 'Image must be under 5MB.' };
  }

  try {
    const { width, height } = await readImageDimensions(file);
    if (width < MIN_WIDTH || height < MIN_HEIGHT) {
      return {
        ok: false,
        message: 'Use an image that is at least 1200x630 for social sharing.',
      };
    }

    const ratio = width / height;
    if (Math.abs(ratio - TARGET_RATIO) > RATIO_TOLERANCE) {
      return {
        ok: false,
        message: 'Use a landscape image close to 1200x630 for the best share card.',
      };
    }

    return { ok: true, width, height };
  } catch {
    return {
      ok: false,
      message: 'Could not read the image. Use a standard raster image at 1200x630.',
    };
  }
}
