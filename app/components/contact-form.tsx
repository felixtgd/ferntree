'use client'

import { sendEmail } from "@/app/utils/helpers";
import { EmailFormData } from "../utils/definitions";
import { useState } from "react";
import { Button, Select, SelectItem, Textarea, TextInput } from "@tremor/react";
import { RiMailSendLine, RiRefreshLine } from "@remixicon/react";
import { useFormStatus } from "react-dom";


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

      const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (formData: FormData) => {
        await sendEmail(formData);
        setIsSubmitted(true);
    }

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
        <form action={handleSubmit} className="max-w-md w-full mx-auto">

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
                        required
                        >
                        <SelectItem value="feedback">Feedback</SelectItem>
                        <SelectItem value="feature">Feature Request</SelectItem>
                        <SelectItem value="bug">Bug Report</SelectItem>
                        <SelectItem value="question">Question</SelectItem>
                        <SelectItem value="general">General</SelectItem>
                    </Select>
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
            </div>

            <div className="mt-6 flex justify-center gap-4">
                <SubmitButton />
            </div>
        </form>
    );
}
