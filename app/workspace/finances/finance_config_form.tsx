'use client';

import { Select, SelectItem, NumberInput, Flex, Button } from "@tremor/react";
import { ModelData } from "@/app/utils/definitions";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
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
    RiShapesLine,
    RiSunLine,
    RiSwap2Line,
    RiToolsLine,
} from "@remixicon/react";

const default_values = {
    // Source: https://www.ise.fraunhofer.de/de/veroeffentlichungen/studien/aktuelle-fakten-zur-photovoltaik-in-deutschland.html
    electr_price: 45,
    feed_in_tariff: 8,
    pv_price_kwp: 1500,
    bat_price_kwh: 650,
    useful_life: 20,
    module_deg: 0.5,
    inflation: 2,
    op_cost: 1,
    down_payment: 20,
    pay_off_rate: 5,
    interest_rate: 4
}

export function FinanceConfigForm({models}: {models: ModelData[]}) {

    const [showAdvanced, setShowAdvanced] = useState(false);

    const toggleAdvanced = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        setShowAdvanced(!showAdvanced);
    };

    const [modelData, setModelData] = useState(models[0]);
    const params = useParams();

    useEffect(() => {
        if (params.model_id) {
            console.log(`ModelSelectForm: Setting model data from URL: ${params.model_id}`);
            const model_id = params.model_id as string;
            const selectedModel = models.find((model) => model.model_id === model_id);
            if (selectedModel) {
                setModelData(selectedModel);
            }
        }
    }, [params.model_id, models]);

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        console.log(event.target.value);
    };

    return (
        <div className="flex flex-col w-full items-center">
            <form className="w-full">
                <h2 className="w-full text-center mb-4">
                    Select a model and enter your financial parameters
                </h2>

                <div className="mb-4 w-full relative">
                    <Select
                        id="model"
                        name="model"
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
                            placeholder={default_values.electr_price.toString()}
                            icon={RiCoinsLine}
                            onChange={handleChange}
                            // value = {formData.electr_price}
                        />
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
                            placeholder={default_values.feed_in_tariff.toString()}
                            icon={RiSwap2Line}
                            onChange={handleChange}
                            // value = {formData.electr_price}
                        />
                    </div>
                </div>

                {/* PV price per kWp */}
                <div className="mb-4">
                    <label htmlFor="pv_price_kwp" className="mb-2 block text-sm font-medium">
                        PV price per kWp  [€/kWp]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="pv_price_kwp"
                            name="pv_price_kwp"
                            step="1"
                            placeholder={default_values.pv_price_kwp.toString()}
                            icon={RiSunLine}
                            onChange={handleChange}
                            // value = {formData.electr_price}
                        />
                    </div>
                </div>

                {/* Battery price per kWh */}
                <div className="mb-4">
                    <label htmlFor="bat_price_kwh" className="mb-2 block text-sm font-medium">
                        Battery price per kWh  [€/kWh]
                    </label>
                    <div className="relative">
                        <NumberInput
                            id="bat_price_kwh"
                            name="bat_price_kwh"
                            step="1"
                            placeholder={default_values.bat_price_kwh.toString()}
                            icon={RiBattery2ChargeLine}
                            onChange={handleChange}
                            // value = {default_values.bat_price_kwh}
                            disabled={modelData.battery_cap === 0}
                        />
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
                            placeholder={default_values.useful_life.toString()}
                            icon={RiHourglassLine}
                            onChange={handleChange}
                            value={default_values.useful_life}
                        />
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
                                        placeholder={default_values.module_deg.toString()}
                                        icon={RiArrowRightDownLine}
                                        onChange={handleChange}
                                        value={default_values.module_deg.toString()}
                                    />
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
                                        placeholder={default_values.inflation.toString()}
                                        icon={RiFundsLine}
                                        onChange={handleChange}
                                        value={default_values.inflation.toString()}
                                    />
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
                                        placeholder={default_values.op_cost.toString()}
                                        icon={RiToolsLine}
                                        onChange={handleChange}
                                        value={default_values.op_cost.toString()}
                                    />
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
                                        placeholder={default_values.down_payment.toString()}
                                        icon={RiCurrencyLine}
                                        onChange={handleChange}
                                        value ={default_values.down_payment.toString()}
                                    />
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
                                        placeholder={default_values.pay_off_rate.toString()}
                                        icon={RiHandCoinLine}
                                        onChange={handleChange}
                                        value={default_values.pay_off_rate.toString()}
                                    />
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
                                        placeholder={default_values.interest_rate.toString()}
                                        icon={RiBankLine}
                                        onChange={handleChange}
                                        value={default_values.interest_rate.toString()}
                                    />
                                </div>
                            </div>
                            </>
                        )}
                    </Flex>
                </Flex>

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
