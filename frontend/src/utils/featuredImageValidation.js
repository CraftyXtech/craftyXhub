const MAX_FILE_SIZE = 5 * 1024 * 1024;
const TARGET_WIDTH = 1200;
const TARGET_HEIGHT = 630;
const TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT;

export const FEATURED_IMAGE_GUIDANCE =
  'Add a featured image.';

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file);
    const image = new Image();

    image.onload = () => {
      resolve({ image, width: image.width, height: image.height });
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

  try {
    const { width, height } = await loadImage(file);
    return { ok: true, width, height };
  } catch {
    return {
      ok: false,
      message: 'Could not read the image. Use a standard raster image at 1200x630.',
    };
  }
}

export function getImageFileFromClipboardEvent(event) {
  const clipboardItems = event.clipboardData?.items;
  if (!clipboardItems?.length) {
    return null;
  }

  for (const item of clipboardItems) {
    if (item.kind === 'file' && item.type.startsWith('image/')) {
      return item.getAsFile();
    }
  }

  return null;
}

export async function readImageFileFromClipboard() {
  if (!navigator?.clipboard?.read) {
    throw new Error('Clipboard paste is not supported here.');
  }

  const items = await navigator.clipboard.read();
  for (const item of items) {
    const imageType = item.types.find((type) => type.startsWith('image/'));
    if (!imageType) continue;

    const blob = await item.getType(imageType);
    const extension = imageType.split('/')[1] || 'png';
    return new File([blob], `clipboard-image.${extension}`, {
      type: imageType,
      lastModified: Date.now(),
    });
  }

  throw new Error('No image found in clipboard.');
}

function canvasToBlob(canvas, mimeType, quality) {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), mimeType, quality);
  });
}

function resolveOutputFormat(fileType) {
  if (fileType === 'image/png') return { mimeType: 'image/png', extension: 'png' };
  if (fileType === 'image/webp') return { mimeType: 'image/webp', extension: 'webp' };
  return { mimeType: 'image/jpeg', extension: 'jpg' };
}

function buildNormalizedFilename(name, extension) {
  const baseName = name.replace(/\.[^.]+$/, '') || 'featured-image';
  return `${baseName}-social.${extension}`;
}

export async function normalizeFeaturedImageFile(file) {
  const { image } = await loadImage(file);
  const canvas = document.createElement('canvas');
  canvas.width = TARGET_WIDTH;
  canvas.height = TARGET_HEIGHT;

  const context = canvas.getContext('2d');
  if (!context) {
    throw new Error('Canvas is unavailable in this browser.');
  }

  const sourceRatio = image.width / image.height;
  let sourceWidth = image.width;
  let sourceHeight = image.height;
  let sourceX = 0;
  let sourceY = 0;

  if (sourceRatio > TARGET_RATIO) {
    sourceWidth = image.height * TARGET_RATIO;
    sourceX = (image.width - sourceWidth) / 2;
  } else if (sourceRatio < TARGET_RATIO) {
    sourceHeight = image.width / TARGET_RATIO;
    sourceY = (image.height - sourceHeight) / 2;
  }

  context.drawImage(
    image,
    sourceX,
    sourceY,
    sourceWidth,
    sourceHeight,
    0,
    0,
    TARGET_WIDTH,
    TARGET_HEIGHT
  );

  let { mimeType, extension } = resolveOutputFormat(file.type);
  let quality = mimeType === 'image/png' ? undefined : 0.92;
  let blob = await canvasToBlob(canvas, mimeType, quality);

  if (!blob) {
    throw new Error('Failed to process the image.');
  }

  if (blob.size > MAX_FILE_SIZE && mimeType === 'image/png') {
    mimeType = 'image/jpeg';
    extension = 'jpg';
    quality = 0.92;
    blob = await canvasToBlob(canvas, mimeType, quality);
  }

  while (blob && blob.size > MAX_FILE_SIZE && typeof quality === 'number' && quality > 0.55) {
    quality = Number((quality - 0.08).toFixed(2));
    blob = await canvasToBlob(canvas, mimeType, quality);
  }

  if (!blob || blob.size > MAX_FILE_SIZE) {
    throw new Error('Image must be under 5MB after processing.');
  }

  return new File(
    [blob],
    buildNormalizedFilename(file.name, extension),
    {
      type: mimeType,
      lastModified: Date.now(),
    }
  );
}
