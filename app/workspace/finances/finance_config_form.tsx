'use client';

import { Select, SelectItem, NumberInput, Flex, Button } from "@tremor/react";
import { FinData, FormState, ModelData } from "@/app/utils/definitions";
import { useState, useEffect } from "react";
import { useFormStatus, useFormState } from 'react-dom'
import { useParams } from "next/navigation";
import { submitFinances } from "./actions";
import {
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

export function FinanceConfigForm({models}: {models: ModelData[]}) {

    const [modelData, setModelData] = useState(models[0]);

    const default_fin_data: FinData = {
        // Source: https://www.ise.fraunhofer.de/de/veroeffentlichungen/studien/aktuelle-fakten-zur-photovoltaik-in-deutschland.html
        model_id: modelData.model_id as string,
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


                {/* Electricity price */}
                <div className="mb-4">
                    <label htmlFor="electr_price" className="mb-2 block text-sm font-medium">
                        Electricity price [cents/kWh]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="electr_price"
                            name="electr_price"
                            step="0.1"
                            placeholder={formData.electr_price.toString()}
                            icon={RiCoinsLine}
                            onChange={handleChange}
                            value = {formData.electr_price}
                        />
                    </div>
                    <div id="electr_price_error" aria-live="polite" aria-atomic="true">
                        {state.errors?.electr_price &&
                        state.errors.electr_price.map((error: string) => (
                            <p className="mt-2 text-sm text-red-500" key={error}>
                            {error}
                            </p>
                        ))}
                    </div>
                </div>

                {/* Feed-in tariff */}
                <div className="mb-4">
                    <label htmlFor="feed_in_tariff" className="mb-2 block text-sm font-medium">
                        Feed-in tariff [cents/kWh]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="feed_in_tariff"
                            name="feed_in_tariff"
                            step="0.1"
                            placeholder={formData.feed_in_tariff.toString()}
                            icon={RiSwap2Line}
                            onChange={handleChange}
                            value = {formData.feed_in_tariff}
                        />
                    </div>
                    <div id="feed_in_tariff_error" aria-live="polite" aria-atomic="true">
                        {state.errors?.feed_in_tariff &&
                        state.errors.feed_in_tariff.map((error: string) => (
                            <p className="mt-2 text-sm text-red-500" key={error}>
                            {error}
                            </p>
                        ))}
                    </div>
                </div>

                {/* PV price per kWp */}
                <div className="mb-4">
                    <label htmlFor="pv_price" className="mb-2 block text-sm font-medium">
                        PV price per kWp  [€/kWp]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="pv_price"
                            name="pv_price"
                            step="1"
                            placeholder={formData.pv_price.toString()}
                            icon={RiSunLine}
                            onChange={handleChange}
                            value = {formData.pv_price}
                        />
                    </div>
                    <div id="pv_price_error" aria-live="polite" aria-atomic="true">
                        {state.errors?.pv_price &&
                        state.errors.pv_price.map((error: string) => (
                            <p className="mt-2 text-sm text-red-500" key={error}>
                            {error}
                            </p>
                        ))}
                    </div>
                </div>

                {/* Battery price per kWh */}
                <div className="mb-4">
                    <label htmlFor="battery_price" className="mb-2 block text-sm font-medium">
                        Battery price per kWh  [€/kWh]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="battery_price"
                            name="battery_price"
                            step="1"
                            placeholder={formData.battery_price.toString()}
                            icon={RiBattery2ChargeLine}
                            onChange={handleChange}
                            value = {formData.battery_price}
                            disabled={modelData.battery_cap === 0}
                        />
                    </div>
                    <div id="battery_price_error" aria-live="polite" aria-atomic="true">
                        {state.errors?.battery_price &&
                        state.errors.battery_price.map((error: string) => (
                            <p className="mt-2 text-sm text-red-500" key={error}>
                            {error}
                            </p>
                        ))}
                    </div>
                </div>

                {/* Useful life */}
                <div className="mb-4">
                    <label htmlFor="useful_life" className="mb-2 block text-sm font-medium">
                        Useful life [years]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="useful_life"
                            name="useful_life"
                            step="1"
                            placeholder={formData.useful_life.toString()}
                            icon={RiHourglassLine}
                            onChange={handleChange}
                            value={formData.useful_life}
                        />
                    </div>
                    <div id="useful_life_error" aria-live="polite" aria-atomic="true">
                        {state.errors?.useful_life &&
                        state.errors.useful_life.map((error: string) => (
                            <p className="mt-2 text-sm text-red-500" key={error}>
                            {error}
                            </p>
                        ))}
                    </div>
                </div>


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
                            {/* Module degradation */}
                            <div className="mb-4">
                                <label htmlFor="module_deg" className="mb-2 block text-sm font-medium">
                                    Module degradation [%]
                                </label>
                                <div className="relative">
                                    <NumberInput
                                        id="module_deg"
                                        name="module_deg"
                                        step="0.1"
                                        placeholder={formData.module_deg.toString()}
                                        icon={RiArrowRightDownLine}
                                        onChange={handleChange}
                                        value={formData.module_deg}
                                    />
                                </div>
                                <div id="module_deg_error" aria-live="polite" aria-atomic="true">
                                    {state.errors?.module_deg &&
                                    state.errors.module_deg.map((error: string) => (
                                        <p className="mt-2 text-sm text-red-500" key={error}>
                                        {error}
                                        </p>
                                    ))}
                                </div>
                            </div>

                            {/* Inflation */}
                            <div className="mb-4">
                                <label htmlFor="inflation" className="mb-2 block text-sm font-medium">
                                    Inflation [%]
                                </label>
                                <div className="relative">
                                    <NumberInput
                                        id="inflation"
                                        name="inflation"
                                        step="0.1"
                                        placeholder={formData.inflation.toString()}
                                        icon={RiFundsLine}
                                        onChange={handleChange}
                                        value={formData.inflation}
                                    />
                                </div>
                                <div id="inflation_error" aria-live="polite" aria-atomic="true">
                                    {state.errors?.inflation &&
                                    state.errors.inflation.map((error: string) => (
                                        <p className="mt-2 text-sm text-red-500" key={error}>
                                        {error}
                                        </p>
                                    ))}
                                </div>
                            </div>

                            {/* Operation cost */}
                            <div className="mb-4">
                                <label htmlFor="op_cost" className="mb-2 block text-sm font-medium">
                                    Operation cost [%]
                                </label>
                                <div className="relative">
                                    <NumberInput
                                        id="op_cost"
                                        name="op_cost"
                                        step="0.1"
                                        placeholder={formData.op_cost.toString()}
                                        icon={RiToolsLine}
                                        onChange={handleChange}
                                        value={formData.op_cost}
                                    />
                                </div>
                                <div id="op_cost_error" aria-live="polite" aria-atomic="true">
                                    {state.errors?.op_cost &&
                                    state.errors.op_cost.map((error: string) => (
                                        <p className="mt-2 text-sm text-red-500" key={error}>
                                        {error}
                                        </p>
                                    ))}
                                </div>
                            </div>

                            {/* Down payment */}
                            <div className="mb-4">
                                <label htmlFor="down_payment" className="mb-2 block text-sm font-medium">
                                    Down payment [%]
                                </label>
                                <div className="relative">
                                    <NumberInput
                                        id="down_payment"
                                        name="down_payment"
                                        step="0.1"
                                        placeholder={formData.down_payment.toString()}
                                        icon={RiCurrencyLine}
                                        onChange={handleChange}
                                        value ={formData.down_payment.toString()}
                                    />
                                </div>
                                <div id="down_payment_error" aria-live="polite" aria-atomic="true">
                                    {state.errors?.down_payment &&
                                    state.errors.down_payment.map((error: string) => (
                                        <p className="mt-2 text-sm text-red-500" key={error}>
                                        {error}
                                        </p>
                                    ))}
                                </div>
                            </div>

                            {/* Pay off rate */}
                            <div className="mb-4">
                                <label htmlFor="pay_off_rate" className="mb-2 block text-sm font-medium">
                                    Pay off rate [%]
                                </label>
                                <div className="relative">
                                    <NumberInput
                                        id="pay_off_rate"
                                        name="pay_off_rate"
                                        step="0.1"
                                        placeholder={formData.pay_off_rate.toString()}
                                        icon={RiHandCoinLine}
                                        onChange={handleChange}
                                        value={formData.pay_off_rate}
                                    />
                                </div>
                                <div id="pay_off_rate_error" aria-live="polite" aria-atomic="true">
                                    {state.errors?.pay_off_rate &&
                                    state.errors.pay_off_rate.map((error: string) => (
                                        <p className="mt-2 text-sm text-red-500" key={error}>
                                        {error}
                                        </p>
                                    ))}
                                </div>
                            </div>

                            {/* Interest rate */}
                            <div className="mb-4">
                                <label htmlFor="interest_rate" className="mb-2 block text-sm font-medium">
                                    Interest rate [%]
                                </label>
                                <div className="relative">
                                    <NumberInput
                                        id="interest_rate"
                                        name="interest_rate"
                                        step="0.1"
                                        placeholder={formData.interest_rate.toString()}
                                        icon={RiBankLine}
                                        onChange={handleChange}
                                        value={formData.interest_rate}
                                    />
                                </div>
                                <div id="interest_rate_error" aria-live="polite" aria-atomic="true">
                                    {state.errors?.interest_rate &&
                                    state.errors.interest_rate.map((error: string) => (
                                        <p className="mt-2 text-sm text-red-500" key={error}>
                                        {error}
                                        </p>
                                    ))}
                                </div>
                            </div>
                            </>
                        )}
                    </Flex>
                </Flex>

                {/* Hidden inputs to ensure values are included in form data */}
                {!showAdvanced && (
                    <>
                        <input type="hidden" name="module_deg" value={formData.module_deg} />
                        <input type="hidden" name="inflation" value={formData.inflation} />
                        <input type="hidden" name="op_cost" value={formData.op_cost} />
                        <input type="hidden" name="down_payment" value={formData.down_payment} />
                        <input type="hidden" name="pay_off_rate" value={formData.pay_off_rate} />
                        <input type="hidden" name="interest_rate" value={formData.interest_rate} />
                    </>
                )}

                <div className="mt-6 flex justify-center gap-4">
                    <SubmitButton />
                </div>

            </form>


            {/* <div className="flex flex-col justify-center m-2">
                {modelData.model_id && (
                    modelData.sim_id
                        ? <ViewButton type="model" model_id={modelData.model_id} />
                        : <RunButton type="model" model_id={modelData.model_id} />
                    )
                }
            </div> */}

        </div>
    );
}
