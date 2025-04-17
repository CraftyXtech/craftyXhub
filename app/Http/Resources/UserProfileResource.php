<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserProfileResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'joinedDate' => $this->created_at->isoFormat('YYYY-MM-DD'),
            'avatar' => 'https://via.placeholder.com/150/cccccc/FFFFFF?text=' . substr($this->name, 0, 2), // Placeholder avatar
            // Conditionally load relationships
            'savedArticles' => PostResource::collection($this->whenLoaded('savedPosts')),
            // Add reading history later if implemented
            // 'readingHistory' => ... 
        ];
    }
}
