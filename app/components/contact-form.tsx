'use client'

import { sendEmail } from "@/app/utils/helpers";
import { EmailFormData, FormState } from "../utils/definitions";
import { useState } from "react";
import { Button, Select, SelectItem, Textarea, TextInput } from "@tremor/react";
import { RiMailSendLine, RiRefreshLine } from "@remixicon/react";
import { useFormState, useFormStatus } from "react-dom";
import DOMPurify from 'dompurify';

function SubmitButton() {
    const { pending } = useFormStatus()

    return (
      <Button
        type="submit"
        icon={RiMailSendLine}
        disabled={pending}
        aria-label="Send message"
      >
        Send
      </Button>
    )
  }

export default function ContactForm() {

    const defaultEmailFormData: EmailFormData = {
        name: "",
        email: "",
        category: "",
        message: ""
    };

      const [formData, setFormData] = useState(defaultEmailFormData);
      const [isSubmitted, setIsSubmitted] = useState(false);
      const initialState : FormState = { message: null, errors: {} };

      const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target;
        const sanitized_value = DOMPurify.sanitize(value as string)
        setFormData({ ...formData, [name]: sanitized_value });
    };

    const handleSubmit = async (prev_state: FormState, form_data: FormData) => {
        const state: FormState = await sendEmail(prev_state, form_data);
        if (state.message === 'success')
            setIsSubmitted(true);
        return state;
    }

    const [state, formAction] = useFormState(handleSubmit, initialState);

    const handleReset = () => {
        setFormData(defaultEmailFormData);
        setIsSubmitted(false);
      };

    if (isSubmitted) {
        return (
        <div className="text-center max-w-md w-full mx-auto">
            <p className="text-green-600 mb-4">
                Thank you for your message. We&apos;ll get back to you soon!
            </p>
            <Button onClick={handleReset} icon={RiRefreshLine}>
                Send another message
            </Button>
        </div>
        );
    }

    return (
        <form action={formAction} className="max-w-md w-full mx-auto">

            {/* Name */}
            <div className="mb-4">
                <label htmlFor="name" className="mb-2 ml-2 block text-sm font-medium">
                    Name
                </label>
                <div className="relative">
                    <TextInput
                    id="name"
                    name="name"
                    type="text"
                    onChange={handleChange}
                    placeholder="(optional)"
                    />
                </div>
                <div id="name-error" aria-live="polite" aria-atomic="true">
                    {state.errors?.name &&
                    state.errors.name.map((error: string) => (
                        <p className="mt-2 ml-2 text-sm text-red-500" key={error}>
                        {error}
                        </p>
                    ))}
                </div>
            </div>

            {/* E-Mail */}
            <div className="mb-4">
                <label htmlFor="email" className="mb-2 ml-2 block text-sm font-medium">
                    E-Mail
                </label>
                <div className="relative">
                    <TextInput
                    id="email"
                    name="email"
                    type="text"
                    onChange={handleChange}
                    placeholder="(optional)"
                    />
                </div>
                <div id="email-error" aria-live="polite" aria-atomic="true">
                    {state.errors?.email &&
                    state.errors.email.map((error: string) => (
                        <p className="mt-2 ml-2 text-sm text-red-500" key={error}>
                        {error}
                        </p>
                    ))}
                </div>
            </div>

            {/* Category */}
            <div className="mb-4">
                <label htmlFor="category" className="mb-2 ml-2 block text-sm font-medium">
                    Category
                </label>
                <div className="relative">
                    <Select
                        id="category"
                        name="category"
                        onValueChange={
                            (value: string) => {
                            setFormData({ ...formData, category: value });
                            }
                        }
                        value = {formData.category.toString()}
                        // required
                        >
                        <SelectItem value="feedback">Feedback</SelectItem>
                        <SelectItem value="feature">Feature Request</SelectItem>
                        <SelectItem value="bug">Bug Report</SelectItem>
                        <SelectItem value="question">Question</SelectItem>
                        <SelectItem value="general">General</SelectItem>
                    </Select>
                </div>
                <div id="category-error" aria-live="polite" aria-atomic="true">
                    {state.errors?.category &&
                    state.errors.category.map((error: string) => (
                        <p className="mt-2 ml-2 text-sm text-red-500" key={error}>
                        {error}
                        </p>
                    ))}
                </div>
            </div>

            {/* Message */}
            <div className="mb-4">
                <label htmlFor="message" className="mb-2 ml-2 block text-sm font-medium">
                    Message
                </label>
                <div className="relative">
                    <Textarea
                    id="message"
                    name="message"
                    placeholder="Your message here"
                    rows={6}
                    />
                </div>
                <div id="message-error" aria-live="polite" aria-atomic="true">
                    {state.errors?.message &&
                    state.errors.message.map((error: string) => (
                        <p className="mt-2 ml-2 text-sm text-red-500" key={error}>
                        {error}
                        </p>
                    ))}
                </div>
            </div>

            <div className="mt-6 flex justify-center gap-4">
                <SubmitButton />
            </div>
        </form>
    );
}
