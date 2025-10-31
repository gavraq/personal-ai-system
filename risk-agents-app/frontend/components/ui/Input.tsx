/**
 * Input Component
 * Reusable text input component with validation states
 */

'use client';

import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type InputVariant = 'default' | 'error' | 'success' | 'warning';
export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Input variant (affects border color and styling) */
  variant?: InputVariant;
  /** Input size */
  size?: InputSize;
  /** Label text */
  label?: string;
  /** Help text displayed below input */
  helperText?: string;
  /** Error message (automatically sets variant to 'error') */
  error?: string;
  /** Success message (automatically sets variant to 'success') */
  success?: string;
  /** Left icon */
  leftIcon?: ReactNode;
  /** Right icon */
  rightIcon?: ReactNode;
  /** Full width */
  fullWidth?: boolean;
  /** Custom container className */
  containerClassName?: string;
}

/**
 * Input Component
 *
 * A flexible input component with:
 * - Multiple validation states (error, success, warning)
 * - Size variants (sm, md, lg)
 * - Label and helper text support
 * - Left/right icon slots
 * - Full design system integration
 *
 * @example
 * ```tsx
 * <Input
 *   label="Email"
 *   type="email"
 *   placeholder="you@example.com"
 *   helperText="We'll never share your email"
 * />
 *
 * <Input
 *   label="Password"
 *   type="password"
 *   error="Password must be at least 8 characters"
 * />
 *
 * <Input
 *   leftIcon={<SearchIcon />}
 *   placeholder="Search..."
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'default',
      size = 'md',
      label,
      helperText,
      error,
      success,
      leftIcon,
      rightIcon,
      fullWidth = false,
      containerClassName,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    // Determine actual variant based on error/success props
    const actualVariant = error
      ? 'error'
      : success
        ? 'success'
        : variant;

    // Display message (error takes precedence over success, then helperText)
    const displayMessage = error || success || helperText;

    // Size classes
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-5 py-3 text-lg',
    };

    // Icon size classes
    const iconSizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
    };

    // Variant border/ring colors
    const variantClasses = {
      default:
        'border-slate-700 focus:border-blue-500 focus:ring-blue-500/20',
      error: 'border-red-500 focus:border-red-500 focus:ring-red-500/20',
      success:
        'border-green-500 focus:border-green-500 focus:ring-green-500/20',
      warning:
        'border-yellow-500 focus:border-yellow-500 focus:ring-yellow-500/20',
    };

    // Message text color
    const messageColorClasses = {
      default: 'text-slate-400',
      error: 'text-red-400',
      success: 'text-green-400',
      warning: 'text-yellow-400',
    };

    return (
      <div
        className={cn(
          'flex flex-col gap-1.5',
          fullWidth ? 'w-full' : '',
          containerClassName
        )}
      >
        {/* Label */}
        {label && (
          <label className="text-sm font-medium text-slate-300">
            {label}
          </label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div
              className={cn(
                'absolute left-3 top-1/2 -translate-y-1/2 text-slate-400',
                iconSizeClasses[size]
              )}
            >
              {leftIcon}
            </div>
          )}

          {/* Input Field */}
          <input
            ref={ref}
            disabled={disabled}
            className={cn(
              // Base styles
              'w-full rounded-lg border bg-slate-800/50 text-slate-200',
              'placeholder-slate-500 transition-all duration-200',
              'focus:outline-none focus:ring-2',

              // Size
              sizeClasses[size],

              // Variant
              variantClasses[actualVariant],

              // Icon padding
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',

              // Disabled state
              disabled &&
                'cursor-not-allowed opacity-50 bg-slate-800/30',

              className
            )}
            {...props}
          />

          {/* Right Icon */}
          {rightIcon && (
            <div
              className={cn(
                'absolute right-3 top-1/2 -translate-y-1/2 text-slate-400',
                iconSizeClasses[size]
              )}
            >
              {rightIcon}
            </div>
          )}
        </div>

        {/* Helper/Error/Success Message */}
        {displayMessage && (
          <p
            className={cn(
              'text-xs',
              messageColorClasses[actualVariant]
            )}
          >
            {displayMessage}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

/**
 * Textarea Component
 *
 * Similar to Input but for multi-line text
 */
export interface TextareaProps
  extends Omit<
    React.TextareaHTMLAttributes<HTMLTextAreaElement>,
    'size'
  > {
  variant?: InputVariant;
  size?: InputSize;
  label?: string;
  helperText?: string;
  error?: string;
  success?: string;
  fullWidth?: boolean;
  containerClassName?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      variant = 'default',
      size = 'md',
      label,
      helperText,
      error,
      success,
      fullWidth = false,
      containerClassName,
      className,
      disabled,
      rows = 4,
      ...props
    },
    ref
  ) => {
    const actualVariant = error
      ? 'error'
      : success
        ? 'success'
        : variant;
    const displayMessage = error || success || helperText;

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-5 py-3 text-lg',
    };

    const variantClasses = {
      default:
        'border-slate-700 focus:border-blue-500 focus:ring-blue-500/20',
      error: 'border-red-500 focus:border-red-500 focus:ring-red-500/20',
      success:
        'border-green-500 focus:border-green-500 focus:ring-green-500/20',
      warning:
        'border-yellow-500 focus:border-yellow-500 focus:ring-yellow-500/20',
    };

    const messageColorClasses = {
      default: 'text-slate-400',
      error: 'text-red-400',
      success: 'text-green-400',
      warning: 'text-yellow-400',
    };

    return (
      <div
        className={cn(
          'flex flex-col gap-1.5',
          fullWidth ? 'w-full' : '',
          containerClassName
        )}
      >
        {label && (
          <label className="text-sm font-medium text-slate-300">
            {label}
          </label>
        )}

        <textarea
          ref={ref}
          disabled={disabled}
          rows={rows}
          className={cn(
            'w-full rounded-lg border bg-slate-800/50 text-slate-200',
            'placeholder-slate-500 transition-all duration-200',
            'focus:outline-none focus:ring-2 resize-none',
            sizeClasses[size],
            variantClasses[actualVariant],
            disabled &&
              'cursor-not-allowed opacity-50 bg-slate-800/30',
            className
          )}
          {...props}
        />

        {displayMessage && (
          <p className={cn('text-xs', messageColorClasses[actualVariant])}>
            {displayMessage}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

/**
 * FormGroup Component
 *
 * Groups form inputs together with consistent spacing
 */
export interface FormGroupProps {
  children: ReactNode;
  className?: string;
}

export function FormGroup({ children, className }: FormGroupProps) {
  return (
    <div className={cn('flex flex-col gap-4', className)}>{children}</div>
  );
}

/**
 * FieldSet Component
 *
 * Groups related form fields with a legend
 */
export interface FieldSetProps {
  legend?: string;
  children: ReactNode;
  className?: string;
}

export function FieldSet({ legend, children, className }: FieldSetProps) {
  return (
    <fieldset className={cn('border border-slate-700 rounded-lg p-4', className)}>
      {legend && (
        <legend className="px-2 text-sm font-semibold text-slate-300">
          {legend}
        </legend>
      )}
      <div className="flex flex-col gap-4 mt-2">{children}</div>
    </fieldset>
  );
}
