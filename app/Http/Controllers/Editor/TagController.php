<?php

namespace App\Http\Controllers\Editor;

use App\Http\Controllers\Controller;
use App\Models\Tag;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Str;
use Illuminate\Http\RedirectResponse;

class TagController extends Controller
{
    /**
     * Display a listing of the tags.
     *
     * @return Response
     */
    public function index(): Response
    {
        $tags = Tag::withCount('posts')->orderBy('name')->get();
        
        return Inertia::render('Editor/Tags/Index', [
            'tags' => $tags,
        ]);
    }

    /**
     * Show the form for creating a new tag.
     *
     * @return Response
     */
    public function create(): Response
    {
        return Inertia::render('Editor/Tags/Create');
    }

    /**
     * Store a newly created tag in storage.
     *
     * @param Request $request
     * @return RedirectResponse
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255|unique:tags',
            'slug' => 'nullable|string|max:255|unique:tags',
        ]);
        
        // Generate slug if not provided
        if (empty($validated['slug'])) {
            $validated['slug'] = Str::slug($validated['name']);
        }
        
        Tag::create($validated);
        
        return redirect()->route('editor.tags.index')
            ->with('success', 'Tag created successfully!');
    }

    /**
     * Show the form for editing the specified tag.
     *
     * @param Tag $tag
     * @return Response
     */
    public function edit(Tag $tag): Response
    {
        return Inertia::render('Editor/Tags/Edit', [
            'tag' => $tag,
        ]);
    }

    /**
     * Update the specified tag in storage.
     *
     * @param Request $request
     * @param Tag $tag
     * @return RedirectResponse
     */
    public function update(Request $request, Tag $tag): RedirectResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255|unique:tags,name,' . $tag->id,
            'slug' => 'nullable|string|max:255|unique:tags,slug,' . $tag->id,
        ]);
        
        // Generate slug if not provided
        if (empty($validated['slug'])) {
            $validated['slug'] = Str::slug($validated['name']);
        }
        
        $tag->update($validated);
        
        return redirect()->route('editor.tags.index')
            ->with('success', 'Tag updated successfully!');
    }

    /**
     * Remove the specified tag from storage.
     *
     * @param Tag $tag
     * @return RedirectResponse
     */
    public function destroy(Tag $tag): RedirectResponse
    {
        // Check if tag is used in posts
        if ($tag->posts()->count() > 0) {
            return back()->with('error', 'Cannot delete tag that is used in posts.');
        }
        
        $tag->delete();
        
        return redirect()->route('editor.tags.index')
            ->with('success', 'Tag deleted successfully!');
    }

    /**
     * Display the specified tag.
     *
     * @param Tag $tag
     * @return Response
     */
    public function show(Tag $tag): Response
    {
        $tag->load('posts');
        
        return Inertia::render('Editor/Tags/Show', [
            'tag' => $tag,
            'postsCount' => $tag->posts->count(),
        ]);
    }
} 