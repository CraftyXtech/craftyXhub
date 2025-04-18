<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Tag extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'slug',
    ];

    public function posts(): BelongsToMany
    {
        return $this->belongsToMany(Post::class);
    }
    
    /**
     * Get users who follow this tag as a topic.
     */
    public function followers(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'user_topics', 'tag_id', 'user_id')
                    ->withTimestamps();
    }

    public function getRouteKeyName()
    {
        return 'slug';
    }
}