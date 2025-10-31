/**
 * Layout Components
 * Header, Sidebar, Footer, and page layout components
 */

'use client';

import { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

/**
 * PageContainer Component
 *
 * Main page container with max width and padding
 */
export interface PageContainerProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

export function PageContainer({
  children,
  maxWidth = 'xl',
  className,
  ...props
}: PageContainerProps) {
  const maxWidthClasses = {
    sm: 'max-w-3xl',
    md: 'max-w-4xl',
    lg: 'max-w-5xl',
    xl: 'max-w-6xl',
    '2xl': 'max-w-7xl',
    full: 'max-w-full',
  };

  return (
    <div
      className={cn(
        'mx-auto px-4 sm:px-6 lg:px-8 py-6',
        maxWidthClasses[maxWidth],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Header Component
 *
 * Application header with navigation and branding
 */
export interface HeaderProps {
  logo?: ReactNode;
  navigation?: Array<{
    label: string;
    href: string;
    active?: boolean;
  }>;
  actions?: ReactNode;
  className?: string;
}

export function Header({ logo, navigation, actions, className }: HeaderProps) {
  return (
    <header
      className={cn(
        'sticky top-0 z-40 w-full',
        'bg-slate-900/80 backdrop-blur-md',
        'border-b border-slate-800',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-8">
            {logo && (
              <Link href="/" className="flex items-center">
                {logo}
              </Link>
            )}

            {/* Navigation */}
            {navigation && (
              <nav className="hidden md:flex items-center gap-1">
                {navigation.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                      item.active
                        ? 'bg-slate-800 text-slate-200'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    )}
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            )}
          </div>

          {/* Actions */}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      </div>
    </header>
  );
}

/**
 * Sidebar Component
 *
 * Collapsible sidebar navigation
 */
export interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  children?: ReactNode;
  className?: string;
}

export function Sidebar({
  isOpen = true,
  onClose,
  children,
  className,
}: SidebarProps) {
  return (
    <>
      {/* Overlay (mobile) */}
      {isOpen && onClose && (
        <div
          className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50',
          'w-64 bg-slate-900 border-r border-slate-800',
          'transform transition-transform duration-200 ease-in-out',
          'lg:translate-x-0 lg:static lg:z-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          className
        )}
      >
        <div className="h-full flex flex-col">
          {/* Close button (mobile) */}
          {onClose && (
            <div className="flex items-center justify-end p-4 lg:hidden">
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-slate-200 transition-colors"
                aria-label="Close sidebar"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          )}

          {/* Content */}
          <div className="flex-1 overflow-y-auto">{children}</div>
        </div>
      </aside>
    </>
  );
}

/**
 * SidebarNav Component
 *
 * Navigation items for sidebar
 */
export interface SidebarNavProps {
  items: Array<{
    label: string;
    href: string;
    icon?: ReactNode;
    active?: boolean;
    badge?: string | number;
  }>;
  className?: string;
}

export function SidebarNav({ items, className }: SidebarNavProps) {
  return (
    <nav className={cn('space-y-1 p-4', className)}>
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            item.active
              ? 'bg-slate-800 text-slate-200'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          )}
        >
          {/* Icon */}
          {item.icon && <span className="w-5 h-5 flex-shrink-0">{item.icon}</span>}

          {/* Label */}
          <span className="flex-1">{item.label}</span>

          {/* Badge */}
          {item.badge && (
            <span className="badge-ai text-xs">{item.badge}</span>
          )}
        </Link>
      ))}
    </nav>
  );
}

/**
 * Footer Component
 *
 * Application footer
 */
export interface FooterProps {
  copyright?: string;
  links?: Array<{
    label: string;
    href: string;
  }>;
  className?: string;
}

export function Footer({ copyright, links, className }: FooterProps) {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className={cn(
        'w-full border-t border-slate-800 bg-slate-900',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Copyright */}
          <p className="text-sm text-slate-400">
            {copyright || `© ${currentYear} Risk Agents. All rights reserved.`}
          </p>

          {/* Links */}
          {links && (
            <div className="flex items-center gap-6">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-sm text-slate-400 hover:text-slate-200 transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </footer>
  );
}

/**
 * Breadcrumbs Component
 *
 * Standalone breadcrumb navigation
 */
export interface BreadcrumbsProps {
  items: Array<{
    label: string;
    href?: string;
  }>;
  className?: string;
}

export function Breadcrumbs({ items, className }: BreadcrumbsProps) {
  return (
    <nav className={cn('flex items-center gap-2 text-sm text-slate-400 mb-4', className)}>
      {items.map((crumb, index) => (
        <div key={index} className="flex items-center gap-2">
          {index > 0 && <span>/</span>}
          {crumb.href ? (
            <Link
              href={crumb.href}
              className="hover:text-slate-200 transition-colors"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="text-slate-300">{crumb.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}

/**
 * PageHeader Component
 *
 * Page-level header with title and actions
 */
export interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  breadcrumbs?: Array<{
    label: string;
    href?: string;
  }>;
  className?: string;
}

export function PageHeader({
  title,
  description,
  actions,
  breadcrumbs,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn('mb-6', className)}>
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-2 text-sm text-slate-400 mb-2">
          {breadcrumbs.map((crumb, index) => (
            <div key={index} className="flex items-center gap-2">
              {index > 0 && <span>/</span>}
              {crumb.href ? (
                <Link
                  href={crumb.href}
                  className="hover:text-slate-200 transition-colors"
                >
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-slate-300">{crumb.label}</span>
              )}
            </div>
          ))}
        </nav>
      )}

      {/* Title and Actions */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h1 className="font-heading text-hero font-bold text-slate-200 mb-2">
            {title}
          </h1>
          {description && (
            <p className="text-slate-400 max-w-3xl">{description}</p>
          )}
        </div>

        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}

/**
 * Section Component
 *
 * Content section with optional header
 */
export interface SectionProps extends HTMLAttributes<HTMLElement> {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children?: ReactNode;
}

export function Section({
  title,
  description,
  actions,
  children,
  className,
  ...props
}: SectionProps) {
  return (
    <section className={cn('mb-8', className)} {...props}>
      {(title || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            {title && (
              <h2 className="font-heading text-2xl font-semibold text-slate-200 mb-1">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-sm text-slate-400">{description}</p>
            )}
          </div>

          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}

      {children}
    </section>
  );
}

/**
 * DashboardLayout Component
 *
 * Complete dashboard layout with sidebar
 */
export interface DashboardLayoutProps {
  sidebar?: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  children?: ReactNode;
}

export function DashboardLayout({
  sidebar,
  header,
  footer,
  children,
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Header */}
      {header}

      <div className="flex-1 flex">
        {/* Sidebar */}
        {sidebar}

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* Footer */}
      {footer}
    </div>
  );
}
