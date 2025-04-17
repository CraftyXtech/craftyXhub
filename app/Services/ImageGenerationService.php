<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Exception;

class ImageGenerationService
{
    protected $apiKey;
    protected $apiUrl; // Example: Gemini generateImage endpoint
    protected $modelName; // Example: models/gemini-pro-vision ? (Check docs for image gen models)

    public function __construct()
    {
        // Load API key and model details from config/env
        $this->apiKey = config('services.gemini.api_key');
        $this->modelName = config('services.gemini.image_model', 'models/image-generation-001'); // Placeholder model name
        // Example URL - Adjust based on actual Gemini image generation API
        $this->apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/{$this->modelName}:generateImage"; // Placeholder URL

        // Ensure the storage directory exists
        Storage::disk('public')->makeDirectory('generated_images');
    }

    /**
     * Generates an image based on a prompt using an external API, 
     * saves it to public storage, and returns the relative path.
     *
     * @param string $prompt The text prompt for image generation.
     * @param string $postId Optional: Used for generating a unique filename.
     * @return string|null The relative path to the saved image (e.g., 'generated_images/post_123_abc.png') or null on failure.
     */
    public function generateAndSaveImage(string $prompt, string $postId = 'temp'): ?string
    {
        if (empty($this->apiKey)) {
            Log::error('Image Generation Service: API key is not configured.');
            return null;
        }

        if (empty($prompt)) {
            Log::warning('Image Generation Service: Attempted to generate image with empty prompt.');
            return null;
        }

        try {
            Log::info("Image Generation Service: Requesting image for prompt: " . substr($prompt, 0, 100) . '...');

            // --- PLACEHOLDER: Simulate API call and image saving --- 
            /*
            $response = Http::withToken($this->apiKey) // Or appropriate auth
                            ->timeout(120) // Image generation can take longer
                            ->post($this->apiUrl, [
                                'prompt' => [
                                    'text' => $prompt
                                ],
                                'numberOfImages' => 1,
                                'outputFormat' => 'png', // Or jpg
                                // Other parameters like negative prompts, style, aspect ratio etc.
                            ]);

            if ($response->failed()) {
                Log::error('Image Generation Service: API call failed.', [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                return null;
            }

            // --- Process the response --- 
            // This depends heavily on the API's response structure.
            // It might return image data directly (e.g., base64 encoded) or a URL to the image.
            
            // Example: Assuming base64 encoded image data in response
            $imageDataBase64 = $response->json('images.0.imageData'); // Adjust path as needed
            if (!$imageDataBase64) {
                 Log::error('Image Generation Service: No image data found in response.', ['response' => $response->json()]);
                 return null;
            }
            $imageData = base64_decode($imageDataBase64);
            if ($imageData === false) {
                 Log::error('Image Generation Service: Failed to decode base64 image data.');
                 return null;
            }
            
            // Example: If API returns a URL
            // $imageUrl = $response->json('images.0.url');
            // if (!$imageUrl) { ... handle error ... }
            // $imageData = Http::timeout(60)->get($imageUrl)->body(); 
            // if (Http::lastResponse()->failed()) { ... handle error ... }

            */
            
            // --- Start Placeholder --- 
            // Simulate generating image data (e.g., create a simple placeholder image)
            $width = 800;
            $height = 450;
            $image = imagecreatetruecolor($width, $height);
            $bgColor = imagecolorallocate($image, rand(200, 255), rand(200, 255), rand(200, 255)); // Light random bg
            $textColor = imagecolorallocate($image, rand(0, 100), rand(0, 100), rand(0, 100)); // Dark random text
            imagefill($image, 0, 0, $bgColor);
            imagestring($image, 5, 50, $height / 2 - 10, "Placeholder for: " . Str::limit($prompt, 50), $textColor);
            ob_start();
            imagepng($image); // Output PNG data to buffer
            $imageData = ob_get_clean();
            imagedestroy($image);
             // --- End Placeholder --- 
             
            if (empty($imageData)) {
                 Log::error('Image Generation Service: Placeholder image data is empty.');
                 return null;
            }

            // --- Save the image data to storage --- 
            $filename = 'post_' . $postId . '_' . Str::random(8) . '.png'; // Generate unique filename
            $storagePath = 'generated_images/' . $filename;

            if (Storage::disk('public')->put($storagePath, $imageData)) {
                Log::info("Image Generation Service: Image saved successfully to {$storagePath}");
                return $storagePath; // Return the relative path for DB storage
            } else {
                Log::error('Image Generation Service: Failed to save image to storage.', ['path' => $storagePath]);
                return null;
            }

        } catch (Exception $e) {
            Log::error('Image Generation Service: Exception occurred.', [
                'message' => $e->getMessage(),
                'trace' => Str::limit($e->getTraceAsString(), 1000) // Limit trace length
            ]);
            return null;
        }
    }
} 