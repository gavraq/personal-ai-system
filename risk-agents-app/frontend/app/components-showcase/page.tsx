/**
 * Component Showcase Page
 * Demonstrates all UI components from Module 4.5
 */

'use client';

import { useState } from 'react';
import { Button, IconButton, ButtonGroup } from '@/components/ui/Button';
import { Input, Textarea, FormGroup, FieldSet } from '@/components/ui/Input';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  StatCard,
  InfoCard,
  CardGrid,
} from '@/components/ui/Card';
import {
  Spinner,
  LoadingText,
  Skeleton,
  SkeletonCard,
  ProgressBar,
  DotsLoader,
  LoadingState,
} from '@/components/ui/Loading';
import { useToast, useToastHelpers } from '@/components/ui/Toast';
import {
  PageContainer,
  PageHeader,
  Section,
} from '@/components/ui/Layout';

export default function ComponentsShowcasePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(45);
  const { addToast } = useToast();
  const { success, error, warning, info } = useToastHelpers();

  return (
    <PageContainer maxWidth="2xl">
      <PageHeader
        title="Component Showcase"
        description="All UI components from Module 4.5 - Base Components"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'Components' },
        ]}
      />

      {/* Buttons */}
      <Section title="Buttons" description="All button variants and states">
        <CardGrid cols={2}>
          <Card>
            <CardHeader>
              <CardTitle as="h4">Button Variants</CardTitle>
              <CardDescription>6 different button styles</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="gradient">Gradient</Button>
                <Button variant="danger">Danger</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle as="h4">Button Sizes & States</CardTitle>
              <CardDescription>Different sizes and loading states</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex items-center gap-2">
                  <Button size="sm">Small</Button>
                  <Button size="md">Medium</Button>
                  <Button size="lg">Large</Button>
                </div>
                <div className="flex gap-2">
                  <Button isLoading>Loading</Button>
                  <Button disabled>Disabled</Button>
                </div>
                <ButtonGroup>
                  <Button variant="outline">Left</Button>
                  <Button variant="outline">Middle</Button>
                  <Button variant="outline">Right</Button>
                </ButtonGroup>
              </div>
            </CardContent>
          </Card>
        </CardGrid>
      </Section>

      {/* Inputs */}
      <Section title="Inputs" description="Form inputs with validation states">
        <Card>
          <CardContent>
            <FormGroup>
              <Input
                label="Default Input"
                placeholder="Enter text..."
                helperText="This is a helper text"
              />

              <Input
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                success="Email looks good!"
              />

              <Input
                label="Password"
                type="password"
                error="Password must be at least 8 characters"
              />

              <Textarea
                label="Description"
                rows={3}
                placeholder="Enter description..."
              />

              <FieldSet legend="Personal Information">
                <Input label="First Name" placeholder="John" />
                <Input label="Last Name" placeholder="Doe" />
              </FieldSet>
            </FormGroup>
          </CardContent>
        </Card>
      </Section>

      {/* Cards */}
      <Section title="Cards" description="Card layouts and variants">
        <CardGrid cols={3}>
          <Card variant="default">
            <CardHeader>
              <CardTitle as="h4">Default Card</CardTitle>
              <CardDescription>Basic card style</CardDescription>
            </CardHeader>
            <CardContent>Card content goes here</CardContent>
          </Card>

          <Card variant="glass">
            <CardHeader>
              <CardTitle as="h4">Glass Card</CardTitle>
              <CardDescription>Glass morphism style</CardDescription>
            </CardHeader>
            <CardContent>Beautiful glassmorphism effect</CardContent>
          </Card>

          <Card variant="elevated">
            <CardHeader>
              <CardTitle as="h4">Elevated Card</CardTitle>
              <CardDescription>With shadow and hover</CardDescription>
            </CardHeader>
            <CardContent>Hover to see lift effect</CardContent>
          </Card>
        </CardGrid>

        <CardGrid cols={2} className="mt-4">
          <StatCard
            title="Total Users"
            value="1,234"
            icon={<span>👥</span>}
            trend={{ value: 12.5, isPositive: true }}
          />

          <InfoCard
            icon={<span>ℹ️</span>}
            title="Information"
            description="This is an informational card with an icon"
            variant="info"
          />
        </CardGrid>
      </Section>

      {/* Loading States */}
      <Section title="Loading States" description="Spinners, skeletons, and progress">
        <CardGrid cols={2}>
          <Card>
            <CardHeader>
              <CardTitle as="h4">Spinners</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <Spinner size="xs" />
                <Spinner size="sm" />
                <Spinner size="md" />
                <Spinner size="lg" />
                <Spinner size="xl" />
              </div>
              <div className="mt-4">
                <LoadingText text="Loading data..." />
              </div>
              <div className="mt-4">
                <DotsLoader />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle as="h4">Skeletons</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton variant="circular" className="w-12 h-12" />
                <Skeleton variant="text" count={3} />
              </div>
            </CardContent>
          </Card>
        </CardGrid>

        <Card className="mt-4">
          <CardHeader>
            <CardTitle as="h4">Progress Bars</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <ProgressBar value={progress} showLabel variant="primary" />
              <ProgressBar value={75} variant="success" />
              <ProgressBar value={90} variant="warning" />
              <ProgressBar value={50} variant="error" />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() => setProgress(Math.max(0, progress - 10))}
                >
                  Decrease
                </Button>
                <Button
                  size="sm"
                  onClick={() => setProgress(Math.min(100, progress + 10))}
                >
                  Increase
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="mt-4">
          <SkeletonCard />
        </div>
      </Section>

      {/* Toasts */}
      <Section title="Toast Notifications" description="Show notifications to users">
        <Card>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="primary"
                onClick={() => info('This is an info message')}
              >
                Show Info
              </Button>
              <Button
                variant="gradient"
                onClick={() => success('Operation completed successfully!')}
              >
                Show Success
              </Button>
              <Button
                variant="outline"
                onClick={() => warning('Please be careful with this action')}
              >
                Show Warning
              </Button>
              <Button
                variant="danger"
                onClick={() => error('An error occurred!')}
              >
                Show Error
              </Button>
              <Button
                variant="secondary"
                onClick={() =>
                  addToast({
                    title: 'Custom Toast',
                    message: 'This is a custom toast with a title',
                    variant: 'info',
                    action: {
                      label: 'Undo',
                      onClick: () => console.log('Undo clicked'),
                    },
                  })
                }
              >
                Custom Toast
              </Button>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Loading State Wrapper */}
      <Section title="Loading State Wrapper" description="Conditional rendering helper">
        <Card>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Button onClick={() => setIsLoading(!isLoading)}>
                  Toggle Loading
                </Button>
              </div>

              <LoadingState
                isLoading={isLoading}
                loader={<LoadingText text="Loading content..." />}
              >
                <div className="p-4 bg-slate-800/50 rounded-lg">
                  <p className="text-slate-300">
                    This content is shown when not loading. Try toggling the loading state above!
                  </p>
                </div>
              </LoadingState>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Color Palette */}
      <Section title="Design System" description="Colors and styles from Module 4.1">
        <Card>
          <CardHeader>
            <CardTitle as="h4">Color Palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-5 gap-2">
              <div className="h-20 bg-slate-900 rounded flex items-center justify-center text-xs">
                slate-900
              </div>
              <div className="h-20 bg-slate-800 rounded flex items-center justify-center text-xs">
                slate-800
              </div>
              <div className="h-20 bg-slate-700 rounded flex items-center justify-center text-xs">
                slate-700
              </div>
              <div className="h-20 bg-blue-500 rounded flex items-center justify-center text-xs">
                blue-500
              </div>
              <div className="h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded flex items-center justify-center text-xs">
                gradient
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-4">
          <CardHeader>
            <CardTitle as="h4">Typography</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="font-heading text-hero font-bold">Hero Text (48px)</p>
              <p className="text-3xl font-semibold">Section Heading (30px)</p>
              <p className="text-xl font-medium">Card Title (20px)</p>
              <p className="text-base">Body Text (16px)</p>
              <p className="text-sm text-slate-400">Helper Text (14px)</p>
              <p className="text-xs text-slate-500">Caption (12px)</p>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Effects */}
      <Section title="Visual Effects" description="Hover effects and animations">
        <CardGrid cols={3}>
          <Card className="card-lift" hoverable>
            <CardContent>
              <p className="text-center">Card Lift Effect</p>
              <p className="text-xs text-slate-400 text-center mt-2">Hover over me</p>
            </CardContent>
          </Card>

          <Card variant="glass">
            <CardContent>
              <p className="text-center">Glass Morphism</p>
              <p className="text-xs text-slate-400 text-center mt-2">Frosted glass effect</p>
            </CardContent>
          </Card>

          <Card clickable>
            <CardContent>
              <p className="text-center">Clickable Card</p>
              <p className="text-xs text-slate-400 text-center mt-2">Hover to see border</p>
            </CardContent>
          </Card>
        </CardGrid>
      </Section>
    </PageContainer>
  );
}
