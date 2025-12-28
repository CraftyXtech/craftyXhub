import {
  Box,
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  Avatar,
  Stack,
  IconButton
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconBrandTwitter,
  IconBrandLinkedin,
  IconTarget,
  IconUsers,
  IconHeart,
  IconBulb
} from '@tabler/icons-react';
import SectionHeader from '@/components/SectionHeader';

const MotionBox = motion.create(Box);
const MotionCard = motion.create(Card);

// Team members data
const teamMembers = [
  {
    name: 'Sarah Johnson',
    role: 'Founder & CEO',
    bio: 'Visionary leader with 15+ years in digital media and content strategy.',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop',
    twitter: 'sarahjohnson',
    linkedin: 'sarahjohnson'
  },
  {
    name: 'Michael Chen',
    role: 'Head of Content',
    bio: 'Former journalist with a passion for storytelling and community building.',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop',
    twitter: 'michaelchen',
    linkedin: 'michaelchen'
  },
  {
    name: 'Emily Rodriguez',
    role: 'Lead Designer',
    bio: 'Award-winning designer focused on creating beautiful, intuitive experiences.',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop',
    twitter: 'emilyrodriguez',
    linkedin: 'emilyrodriguez'
  },
  {
    name: 'David Kim',
    role: 'Tech Lead',
    bio: 'Full-stack developer building scalable platforms for millions of readers.',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop',
    twitter: 'davidkim',
    linkedin: 'davidkim'
  }
];

// Values data
const values = [
  {
    icon: IconTarget,
    title: 'Quality First',
    description: 'We curate and publish only the highest quality content from talented writers.'
  },
  {
    icon: IconUsers,
    title: 'Community Driven',
    description: 'Our platform is built by and for our community of passionate creators.'
  },
  {
    icon: IconHeart,
    title: 'Reader Focused',
    description: 'Every decision we make centers around providing value to our readers.'
  },
  {
    icon: IconBulb,
    title: 'Always Learning',
    description: 'We embrace curiosity and encourage continuous growth and exploration.'
  }
];

/**
 * About Page
 */
export default function About() {
  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Decorative circles */}
        <Box
          sx={{
            position: 'absolute',
            top: -100,
            right: -100,
            width: 300,
            height: 300,
            borderRadius: '50%',
            bgcolor: 'rgba(255,255,255,0.05)'
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -50,
            left: -50,
            width: 200,
            height: 200,
            borderRadius: '50%',
            bgcolor: 'rgba(255,255,255,0.03)'
          }}
        />

        <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
          <MotionBox
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            sx={{ textAlign: 'center' }}
          >
            <Typography
              variant="overline"
              sx={{ color: 'accent.main', fontWeight: 600, mb: 2, display: 'block' }}
            >
              About CraftyXHub
            </Typography>
            <Typography
              variant="h2"
              sx={{ fontWeight: 700, mb: 3 }}
            >
              Where Ideas Come to Life
            </Typography>
            <Typography
              variant="h6"
              sx={{ fontWeight: 400, opacity: 0.9, lineHeight: 1.7 }}
            >
              We're on a mission to democratize knowledge sharing by connecting curious minds 
              with insightful stories from writers around the world.
            </Typography>
          </MotionBox>
        </Container>
      </Box>

      {/* Our Story */}
      <Container maxWidth="md" sx={{ py: { xs: 6, md: 10 } }}>
        <MotionBox
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 3 }}>
            Our Story
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
            CraftyXHub started in 2020 with a simple idea: create a space where quality content 
            thrives. We noticed that in the age of clickbait and shallow content, readers were 
            hungry for substance. Writers deserved a platform that valued their craft.
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.8 }}>
            Today, we're proud to host thousands of writers sharing insights on design, 
            technology, startups, productivity, and more. Our community continues to grow, 
            united by a shared love for meaningful content that educates, inspires, and 
            entertains.
          </Typography>
        </MotionBox>
      </Container>

      {/* Values Section */}
      <Box sx={{ bgcolor: 'grey.50', py: { xs: 6, md: 10 } }}>
        <Container maxWidth="lg">
          <SectionHeader
            overline="What We Believe"
            title="Our Values"
            subtitle="The principles that guide everything we do"
          />

          <Grid container spacing={3}>
            {values.map((value, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 3 }} key={value.title}>
                <MotionCard
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  sx={{
                    height: '100%',
                    textAlign: 'center',
                    p: 2,
                    border: 'none',
                    boxShadow: 'none',
                    bgcolor: 'transparent'
                  }}
                >
                  <Box
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 2,
                      bgcolor: 'primary.main',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2
                    }}
                  >
                    <value.icon size={28} />
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {value.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {value.description}
                  </Typography>
                </MotionCard>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Team Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <SectionHeader
          overline="The People"
          title="Meet Our Team"
          subtitle="The passionate individuals behind CraftyXHub"
        />

        <Grid container spacing={4}>
          {teamMembers.map((member, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={member.name}>
              <MotionCard
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                variant="outlined"
                sx={{ textAlign: 'center', p: 3 }}
              >
                <Avatar
                  src={member.avatar}
                  sx={{ width: 100, height: 100, mx: 'auto', mb: 2 }}
                />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {member.name}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: 'accent.main', fontWeight: 500, mb: 1 }}
                >
                  {member.role}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {member.bio}
                </Typography>
                <Stack direction="row" spacing={1} justifyContent="center">
                  <IconButton
                    size="small"
                    component="a"
                    href={`https://twitter.com/${member.twitter}`}
                    target="_blank"
                    sx={{ color: '#1DA1F2' }}
                  >
                    <IconBrandTwitter size={18} />
                  </IconButton>
                  <IconButton
                    size="small"
                    component="a"
                    href={`https://linkedin.com/in/${member.linkedin}`}
                    target="_blank"
                    sx={{ color: '#0077B5' }}
                  >
                    <IconBrandLinkedin size={18} />
                  </IconButton>
                </Stack>
              </MotionCard>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box
        sx={{
          bgcolor: 'grey.900',
          color: 'white',
          py: { xs: 6, md: 8 },
          textAlign: 'center'
        }}
      >
        <Container maxWidth="sm">
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 2 }}>
            Ready to Join Us?
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.8 }}>
            Whether you're a reader looking for great content or a writer ready to share 
            your expertise, we'd love to have you in our community.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
