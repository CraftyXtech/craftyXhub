<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class TestUsersSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Create admin user
        User::firstOrCreate(
            ['email' => 'admin@craftyxhub.com'],
            [
                'name' => 'Admin User',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
                'role' => 'admin',
            ]
        );
        
        // Create editor user
        User::firstOrCreate(
            ['email' => 'editor@craftyxhub.com'],
            [
                'name' => 'Editor User',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
                'role' => 'editor',
            ]
        );
        
        // Create regular users
        for ($i = 1; $i <= 10; $i++) {
            User::firstOrCreate(
                ['email' => "user{$i}@craftyxhub.com"],
                [
                    'name' => "Test User {$i}",
                    'password' => Hash::make('password'),
                    'email_verified_at' => now(),
                    'role' => 'user',
                ]
            );
        }
        
        $this->command->info('Test users seeded successfully!');
    }
} 