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
        $admin = User::updateOrCreate(
            ['email' => 'admin@example.com'], // Find by email to avoid duplicates
            [
                'name' => 'Admin User',
                'email' => 'admin@example.com',
                'password' => Hash::make('password'), // Use a secure password
                'role' => 'admin', // Assign admin role
                'email_verified_at' => now(),
            ]
        );

        // Create Primary Editor User
        $primaryEditor = User::updateOrCreate(
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
        $regularUser = User::updateOrCreate(
            ['email' => 'user@example.com'], // Find by email to avoid duplicates
            [
                'name' => 'Regular User',
                'email' => 'user@example.com',
                'password' => Hash::make('password'), // Use a secure password
                'role' => 'user', // Assign default user role (or null if 'user' isn't explicit)
                'email_verified_at' => now(),
            ]
        );

        // Create 5 additional regular users
        for ($i = 1; $i <= 5; $i++) {
            User::updateOrCreate(
                ['email' => "user{$i}@example.com"],
                [
                    'name' => "Regular User {$i}",
                    'email' => "user{$i}@example.com",
                    'password' => Hash::make('password'),
                    'role' => 'user',
                    'email_verified_at' => now(),
                    'bio' => "I'm Regular User {$i}, interested in the platform content.",
                ]
            );
        }

        // Create 5 additional editors
        for ($i = 1; $i <= 5; $i++) {
            User::updateOrCreate(
                ['email' => "editor{$i}@example.com"],
                [
                    'name' => "Editor {$i}",
                    'email' => "editor{$i}@example.com",
                    'password' => Hash::make('password'),
                    'role' => 'editor',
                    'email_verified_at' => now(),
                    'bio' => "I'm Editor {$i}, contributing quality content in my area of expertise.",
                ]
            );
        }
    }
}
