<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class TagResource extends JsonResource
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
            'slug' => $this->slug,
            'followersCount' => $this->whenCounted('followers'),
            'postsCount' => $this->whenCounted('posts'),
            'isFollowing' => $this->when($request->user(), function () use ($request) {
                return $request->user()->isFollowingTopic($this->resource);
            }),
        ];
    }
}
