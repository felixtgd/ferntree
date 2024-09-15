'use client';

import { Select, SelectItem, NumberInput, Flex, Button } from "@tremor/react";
import { FinData, FormState, ModelData } from "@/app/utils/definitions";
import { useState, useEffect } from "react";
import { useFormStatus, useFormState } from 'react-dom'
import { useParams } from "next/navigation";
import { submitFinances } from "./actions";
import {
    RemixiconComponentType,
    RiArrowDownWideLine,
    RiArrowRightDownLine,
    RiArrowUpWideLine,
    RiBankLine,
    RiBattery2ChargeLine,
    RiCoinsLine,
    RiCurrencyLine,
    RiFundsLine,
    RiHandCoinLine,
    RiHourglassLine,
    RiPlayLargeLine,
    RiShapesLine,
    RiSunLine,
    RiSwap2Line,
    RiToolsLine,
} from "@remixicon/react";


function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <Button
      type="submit"
      icon={RiPlayLargeLine}
      disabled={pending}
    >
      Calculate Finances
    </Button>
  )
}

function NumberInputField(
    {
        id,
        label,
        step,
        value,
        icon,
        handleChange,
        errors
    }: {
        id: string,
        label: string,
        step: string,
        value: number,
        icon: RemixiconComponentType,
        handleChange: (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void,
        errors: string[] | undefined
    }
) {

    return (
        <div className="mb-4">
            <label htmlFor="feed_in_tariff" className="mb-2 block text-sm font-medium">
                {label}
            </label>
            <div className="relative">
                <NumberInput
                    id={id}
                    name={id}
                    step={step}
                    placeholder={value.toString()}
                    icon={icon}
                    onChange={handleChange}
                    value = {value}
                />
            </div>
            {errors && (
                <div id={`${id}_error`} aria-live="polite" aria-atomic="true">
                    {errors.map((error, index) => (
                        <p className="mt-2 text-sm text-red-500" key={index}>
                            {error}
                        </p>
                    ))}
                </div>
            )}
        </div>
    )
}



export function FinanceConfigForm({models}: {models: ModelData[]}) {

    const [modelData, setModelData] = useState(models[0]);

    const default_fin_data: FinData = {
        // Source: https://www.ise.fraunhofer.de/de/veroeffentlichungen/studien/aktuelle-fakten-zur-photovoltaik-in-deutschland.html
        model_id: modelData.model_id ? modelData.model_id : "",
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

    const [formData, setFormData] = useState(default_fin_data);
    const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target;
        setFormData({ ...formData, [name]: value });
    };

    const initialState : FormState = { message: null, errors: {} };
    const [state, formAction] = useFormState(submitFinances, initialState);

    // Collapsible for advanced settings
    const [showAdvanced, setShowAdvanced] = useState(false);
    const toggleAdvanced = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        setShowAdvanced(!showAdvanced);
    };

    // Select model data from URL
    const params = useParams();
    useEffect(() => {
        if (params.model_id) {
            console.log(`ModelSelectForm: Setting model data from URL: ${params.model_id}`);
            const model_id = params.model_id as string;
            const selectedModel = models.find((model) => model.model_id === model_id);
            if (selectedModel) {
                setModelData(selectedModel);
                setFormData({
                    ...formData,
                    model_id: model_id
                });
            }
        }
    }, [params.model_id, models, formData]);


    const input_fields = [
        {
            id: "electr_price",
            label: "Electricity price [cents/kWh]",
            step: "0.1",
            value: formData.electr_price,
            icon: RiCoinsLine,
            errors: state.errors?.electr_price
        },
        {
            id: "feed_in_tariff",
            label: "Feed-in tariff [cents/kWh]",
            step: "0.1",
            value: formData.feed_in_tariff,
            icon: RiSwap2Line,
            errors: state.errors?.feed_in_tariff
        },
        {
            id: "pv_price",
            label: "PV price per kWp  [€/kWp]",
            step: "1",
            value: formData.pv_price,
            icon: RiSunLine,
            errors: state.errors?.pv_price
        },
        {
            id: "battery_price",
            label: "Battery price per kWh  [€/kWh]",
            step: "1",
            value: formData.battery_price,
            icon: RiBattery2ChargeLine,
            errors: state.errors?.battery_price
        },
        {
            id: "useful_life",
            label: "Useful life [years]",
            step: "1",
            value: formData.useful_life,
            icon: RiHourglassLine,
            errors: state.errors?.useful_life
        }
    ]

    const advanced_input_fields = [
        {
            id: "module_deg",
            label: "Module degradation [%]",
            step: "0.1",
            value: formData.module_deg,
            icon: RiArrowRightDownLine,
            errors: state.errors?.module_deg
        },
        {
            id: "inflation",
            label: "Inflation [%]",
            step: "0.1",
            value: formData.inflation,
            icon: RiFundsLine,
            errors: state.errors?.inflation
        },
        {
            id: "op_cost",
            label: "Operation cost [%]",
            step: "0.1",
            value: formData.op_cost,
            icon: RiToolsLine,
            errors: state.errors?.op_cost
        },
        {
            id: "down_payment",
            label: "Down payment [%]",
            step: "0.1",
            value: formData.down_payment,
            icon: RiCurrencyLine,
            errors: state.errors?.down_payment
        },
        {
            id: "pay_off_rate",
            label: "Pay off rate [%]",
            step: "0.1",
            value: formData.pay_off_rate,
            icon: RiHandCoinLine,
            errors: state.errors?.pay_off_rate
        },
        {
            id: "interest_rate",
            label: "Interest rate [%]",
            step: "0.1",
            value: formData.interest_rate,
            icon: RiBankLine,
            errors: state.errors?.interest_rate
        }
    ]

    return (
        <div className="flex flex-col w-full items-center">
            <form
                className="w-full"
                action={formAction}
            >
                <h2 className="w-full text-center mb-4">
                    Select a model and enter your financial parameters
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
                                value={modelData.model_id as string}>{modelData.model_name}
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

                <div className="mt-6 flex justify-center gap-4">
                    <SubmitButton />
                </div>

            </form>

        </div>
    );
}
