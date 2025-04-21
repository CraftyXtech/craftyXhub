<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;
use App\Models\User;

class UserRoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Create Admin User
        User::updateOrCreate(
            ['email' => 'admin@example.com'], // Find by email to avoid duplicates
            [
                'name' => 'Admin User',
                'email' => 'admin@example.com',
                'password' => Hash::make('password'), // Use a secure password
                'role' => 'admin', // Assign admin role
                'email_verified_at' => now(),
            ]
        );

        // Create Editor User
        User::updateOrCreate(
            ['email' => 'editor@example.com'], // Find by email to avoid duplicates
            [
                'name' => 'Editor User',
                'email' => 'editor@example.com',
                'password' => Hash::make('password'), // Use a secure password
                'role' => 'editor', // Assign editor role
                'email_verified_at' => now(),
            ]
        );

        // Create Regular User
        User::updateOrCreate(
            ['email' => 'user@example.com'], // Find by email to avoid duplicates
            [
                'name' => 'Regular User',
                'email' => 'user@example.com',
                'password' => Hash::make('password'), // Use a secure password
                'role' => 'user', // Assign default user role (or null if 'user' isn't explicit)
                'email_verified_at' => now(),
            ]
        );
    }
}
