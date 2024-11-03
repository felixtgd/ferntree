'use client';

import { Select, SelectItem, Flex, Button } from "@tremor/react";
import { FinData, FormState, ModelData } from "@/app/utils/definitions";
import { useState, useEffect } from "react";
import { useFormState } from 'react-dom'
import { useParams, useRouter } from "next/navigation";
import { submitFinFormData } from "./actions";
import { get_advanced_input_fields, get_standard_input_fields, NumberInputField, SubmitButton } from "./fin_form_components";
import {
    RiArrowDownWideLine,
    RiArrowUpWideLine,
    RiShapesLine,
} from "@remixicon/react";
import Link from "next/link";
import { ViewSimButton } from "@/app/components/buttons";


function getFinFormDataForModel(model_id: string, fin_form_data_all: FinData[]): FinData {

    // Default financial data for the form
    const default_fin_form_data: FinData = {
        // Source: https://www.ise.fraunhofer.de/de/veroeffentlichungen/studien/aktuelle-fakten-zur-photovoltaik-in-deutschland.html
        model_id: "",
        electr_price: 45,
        feed_in_tariff: 8,
        pv_price: 1500,
        battery_price: 650,
        useful_life: 20,
        module_deg: 0.5,
        inflation: 3,
        op_cost: 1,
        down_payment: 25,
        pay_off_rate: 10,
        interest_rate: 5,
    }

    // Get form data where model_id matches the selected model, or use default data
    const fin_form_data_model: FinData | undefined = fin_form_data_all.find((data) => data.model_id === model_id) as FinData;
    let fin_form_data: FinData;
    if (fin_form_data_model) {
        fin_form_data = fin_form_data_model
    }
    else {
        fin_form_data = default_fin_form_data
    }

    return fin_form_data;
}


export function FinanceConfigForm({models, fin_form_data_all}: {models: ModelData[], fin_form_data_all: FinData[]}) {

    const router = useRouter();

    // Get model data from URL if model_id is provided
    const params = useParams<{ model_id?: string }>();
    let model_data: ModelData
    if (params.model_id && models.length > 0) {
        console.log(`FinanceConfigForm: Setting model data from URL: ${params.model_id}`);
        model_data = models.find((model) => model.model_id === params.model_id) as ModelData;
    }
    else {
        model_data = models[0];
    }

    const [modelData, setModelData] = useState(model_data);

    const fin_form_data: FinData = getFinFormDataForModel(modelData.model_id as string, fin_form_data_all);
    const [formData, setFormData] = useState(fin_form_data);
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

                                const fin_form_data: FinData = getFinFormDataForModel(selectedModel.model_id as string, fin_form_data_all);
                                setFormData(fin_form_data);
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
                        tooltip={field.tooltip}
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
                                        tooltip={field.tooltip}
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
                        Please <Link href={`/workspace/simulations/${modelData.model_id}`} className="font-bold underline">run a simulation</Link> before calculating finances.
                    </p>
                )}

                <div className="mt-6 flex justify-center gap-4">
                    <SubmitButton sim_exists={(modelData.sim_id !== null)} />
                </div>

            </form>

            {(modelData.sim_id) && (
                <div className="mt-4 flex justify-center">
                    <ViewSimButton model_id={modelData.model_id as string} />
                </div>
            )}

        </div>
    );
}
