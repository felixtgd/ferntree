'use client'

import { sendEmail } from "@/app/utils/helpers";
import { EmailFormData, FormState } from "../utils/definitions";
import { useOptimistic, useState } from "react";
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

    type OptimisticFormState = {
        isSubmitted: boolean;
    };

    const [optimisticFormState, addOptimisticFormState] = useOptimistic<
            OptimisticFormState,
            Partial<OptimisticFormState>
        >(
        { isSubmitted: false },
        (state: OptimisticFormState, newState: Partial<OptimisticFormState>) => ({ ...state, ...newState })
    );

    const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target;
        const sanitized_value = DOMPurify.sanitize(value as string)
        setFormData({ ...formData, [name]: sanitized_value });
    };

    const handleSubmit = async (prev_state: FormState, form_data: FormData) => {
        addOptimisticFormState({ isSubmitted: true });
        const state: FormState = await sendEmail(prev_state, form_data);
        if (state.message === 'success')
            setIsSubmitted(true);
        return state;
    }

    const [state, formAction] = useFormState(handleSubmit, initialState);

    const handleReset = () => {
        setFormData(defaultEmailFormData);
        setIsSubmitted(false);
        addOptimisticFormState({ isSubmitted: false });
    };

    if (optimisticFormState.isSubmitted || isSubmitted) {
        return (
        <div className="h-[300px] text-center max-w-md w-full mx-auto">
            <p className="text-blue-600 mb-4">
                Thank you for your message. We&apos;ll get back to you soon!
            </p>
            {isSubmitted && (
                <Button onClick={handleReset} icon={RiRefreshLine}>
                    Send another message
                </Button>
            )}
        </div>
        );
    }

    return (
        <form action={formAction} className="max-w-md w-full mx-auto">

            {/* Name */}
            <div className="mb-4">
                <div className="relative">
                    <TextInput
                    id="name"
                    name="name"
                    type="text"
                    onChange={handleChange}
                    placeholder="Name"
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
                <div className="relative">
                    <TextInput
                    id="email"
                    name="email"
                    type="text"
                    onChange={handleChange}
                    placeholder="E-mail"
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
