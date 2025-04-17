<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Carbon\Carbon;

class CommentResource extends JsonResource
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
            'body' => $this->body,
            'author' => $this->whenLoaded('user', fn() => [
                'name' => $this->user->name,
                 // Add avatar later if users have avatars
                'avatar' => 'https://via.placeholder.com/40/cccccc/FFFFFF?text=' . substr($this->user->name, 0, 2) 
            ]),
            'date' => $this->created_at->diffForHumans(), // Human readable date
            'created_at' => $this->created_at,
            'replies' => CommentResource::collection($this->whenLoaded('replies')), // Recursively load replies
            // Add parent_id if needed for frontend logic
            // 'parent_id' => $this->parent_id,
        ];
    }
}
