"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { X, LoaderCircle } from "lucide-react";
import { clsx } from "clsx";
import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({ className, variant = "secondary", busy, children, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "danger"; busy?: boolean }) {
  return <button className={clsx("button", `button-${variant}`, className)} {...props} disabled={props.disabled || busy}>{busy && <LoaderCircle size={15} className="spin" />}{children}</button>;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "warning" | "danger" | "blue" }) {
  return <span className={clsx("badge", `badge-${tone}`)}>{children}</span>;
}

export function Modal({ open, onClose, title, description, children, wide = false, drawer = false }: { open: boolean; onClose: () => void; title: string; description?: string; children: ReactNode; wide?: boolean; drawer?: boolean }) {
  return <Dialog.Root open={open} onOpenChange={value => !value && onClose()}><Dialog.Portal><Dialog.Overlay className="modal-overlay" /><Dialog.Content className={clsx("modal", { "modal-wide": wide, drawer })}><div className="modal-heading"><div><Dialog.Title>{title}</Dialog.Title><Dialog.Description>{description || "Review details and make changes to your private workspace."}</Dialog.Description></div><Dialog.Close asChild><button className="icon-button" aria-label="Close dialog"><X size={20} /></button></Dialog.Close></div>{children}</Dialog.Content></Dialog.Portal></Dialog.Root>;
}

export function Field({ label, children, hint }: { label: string; children: ReactNode; hint?: string }) {
  return <label className="field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}
