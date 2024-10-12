'use client';

import { Select, SelectItem, Flex, Button } from "@tremor/react";
import { FinData, FormState, ModelData } from "@/app/utils/definitions";
import { useState, useEffect } from "react";
import { useFormState } from 'react-dom'
import { useRouter } from "next/navigation";
import { submitFinFormData } from "./actions";
import { get_advanced_input_fields, get_standard_input_fields, NumberInputField, SubmitButton } from "./fin_form_components";
import {
    RiArrowDownWideLine,
    RiArrowUpWideLine,
    RiShapesLine,
} from "@remixicon/react";
import Link from "next/link";


// Default financial data for the form
const default_fin_data: FinData = {
    // Source: https://www.ise.fraunhofer.de/de/veroeffentlichungen/studien/aktuelle-fakten-zur-photovoltaik-in-deutschland.html
    model_id: "",
    electr_price: 45,
    feed_in_tariff: 8,
    pv_price: 1500,
    battery_price: 650,
    useful_life: 20,
    module_deg: 0.5,
    inflation: 2,
    op_cost: 1,
    down_payment: 20,
    pay_off_rate: 5,
    interest_rate: 4,
}

export function FinanceConfigForm({models}: {models: ModelData[]}) {

    const router = useRouter();

    const [modelData, setModelData] = useState(models[0]);
    const [formData, setFormData] = useState(default_fin_data);
    const [showAdvanced, setShowAdvanced] = useState(false);

    // Action to submit form data and handle validation errors
    const initialState : FormState = { message: null, errors: {}, model_id: null, timestamp: null };
    const [state, formAction] = useFormState(submitFinFormData, initialState);

    // Form input fields
    const input_fields = get_standard_input_fields({formData, state});
    const advanced_input_fields = get_advanced_input_fields({formData, state});

    // Collapsible for advanced settings
    const toggleAdvanced = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        setShowAdvanced(!showAdvanced);
    };

    // Handle change in form data
    const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target;
        setFormData({ ...formData, [name]: value });
    };

    // Redirect to model results page on successful form submission
    // Refresh the page to display the new fin results after re-submitting the form
    useEffect(() => {
        if (state.message === 'success') {
            router.push(`/workspace/finances/${state.model_id}`);
            router.refresh();
        }
    }, [state, router]);

    // If models is empty list, return div with link to models page
    if (models.length === 0) {
        return (
            <div className="flex flex-col w-full items-center">
                <h2 className="w-full text-center mb-4">
                    Please <Link href="/workspace/models" className="text-blue-500">create a model</Link> first.
                </h2>
            </div>
        );
    }

    return (
        <div className="flex flex-col w-full items-center">
            <form
                className="w-full"
                action={formAction}
            >
                <h2 className="w-full text-center mb-4">
                    Settings
                </h2>

                <div className="mb-4 w-full relative">
                    <Select
                        id="model_id"
                        name="model_id"
                        icon={RiShapesLine}
                        onValueChange={
                            (value: string) => {
                                const selectedModel = models.find((model) => model.model_id === value) as ModelData;
                                setModelData(selectedModel);
                            }
                        }
                        value = {modelData.model_id as string}
                    >
                        {models.map((modelData, index) => (
                            <SelectItem
                                key={index}
                                value={modelData.model_id as string}>
                                    {modelData.model_name}
                            </SelectItem>
                        ))}
                    </Select>
                </div>

                {input_fields.map((field, index) => (
                    <NumberInputField
                        key={index}
                        id={field.id}
                        label={field.label}
                        step={field.step}
                        value={field.value}
                        icon={field.icon}
                        handleChange={handleChange}
                        errors={field.errors}
                    />
                ))}

                <Flex>
                    <Flex flexDirection="col" className="flex items-center">
                        <Button
                            className="mb-4"
                            variant="secondary"
                            onClick={toggleAdvanced}
                            icon={showAdvanced ? RiArrowUpWideLine : RiArrowDownWideLine}>
                            Advanced
                        </Button>
                        {showAdvanced && (
                            <>
                                {advanced_input_fields.map((field, index) => (
                                    <NumberInputField
                                        key={index}
                                        id={field.id}
                                        label={field.label}
                                        step={field.step}
                                        value={field.value}
                                        icon={field.icon}
                                        handleChange={handleChange}
                                        errors={field.errors}
                                    />
                                ))}
                            </>
                        )}
                    </Flex>
                </Flex>

                {/* Hidden inputs to ensure values are included in form data */}
                {!showAdvanced && (
                    <>
                        {advanced_input_fields.map((field, index) => (
                            <input type="hidden" name={field.id} value={field.value} key={index} />
                        ))}
                    </>
                )}

                {(modelData.sim_id == null) && (
                    <p className="mt-4 text-red-500 text-center">
                        Please run a simulation before calculating finances.
                    </p>
                )}

                <div className="mt-6 flex justify-center gap-4">
                    <SubmitButton sim_exists={(modelData.sim_id !== null)} />
                </div>

            </form>
        </div>
    );
}
