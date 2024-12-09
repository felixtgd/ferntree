import { NumberInput, Button } from "@tremor/react";
import { useFormStatus } from 'react-dom'
import LoadingScreen from "@/app/components/loading-screen";
import { FinData, FormState } from "@/app/utils/definitions";
import { Tooltip } from '@/app/components/components';
import {
    RemixiconComponentType,
    RiPlayLargeLine,
    RiArrowRightDownLine,
    RiBankLine,
    RiBattery2ChargeLine,
    RiCoinsLine,
    RiCurrencyLine,
    RiFundsLine,
    RiHandCoinLine,
    RiHourglassLine,
    RiSunLine,
    RiSwap2Line,
    RiToolsLine,
} from "@remixicon/react";




export function SubmitButton({sim_exists}: {sim_exists: boolean}) {
    const { pending } = useFormStatus()

    return (
      <>
      <Button
        type="submit"
        icon={RiPlayLargeLine}
        disabled={pending || !sim_exists}
      >
        Calculate Finances
      </Button>
      {pending && <LoadingScreen message={"Calculating your system's finances ..."} />}
      </>
    )
  }


export function NumberInputField(
    {
        id,
        label,
        tooltip,
        step,
        value,
        icon,
        handleChange,
        errors
    }: {
        id: string,
        label: string,
        tooltip: string,
        step: string,
        value: number,
        icon: RemixiconComponentType,
        handleChange: (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void,
        errors: string[] | undefined
    }
)   {
        return (
            <div className="mb-4">
                <label htmlFor="feed_in_tariff" className="mb-2 block text-sm font-medium">
                    <Tooltip content={tooltip}>
                    <span>{label}</span>
                    </Tooltip>
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


// Input fields for the form
export function get_standard_input_fields({formData, state}: {formData: FinData, state: FormState}) {

    return [
        {
            id: "electr_price",
            label: "Electricity price [ct/kWh]",
            tooltip: "Price of electricity in cents per kilowatt-hour",
            step: "0.1",
            value: formData.electr_price,
            icon: RiCoinsLine,
            errors: state.errors?.electr_price
        },
        {
            id: "feed_in_tariff",
            label: "Feed-in tariff [ct/kWh]",
            tooltip: "Remuneration for electricity fed into the grid in cents per kilowatt-hour",
            step: "0.1",
            value: formData.feed_in_tariff,
            icon: RiSwap2Line,
            errors: state.errors?.feed_in_tariff
        },
        {
            id: "pv_price",
            label: "PV price [€/kWp]",
            tooltip: "Price of installed PV peak generation capacity in euros per kilowatt-peak",
            step: "1",
            value: formData.pv_price,
            icon: RiSunLine,
            errors: state.errors?.pv_price
        },
        {
            id: "battery_price",
            label: "Battery price [€/kWh]",
            tooltip: "Price of installed battery storage capacity in euros per kilowatt-hour",
            step: "1",
            value: formData.battery_price,
            icon: RiBattery2ChargeLine,
            errors: state.errors?.battery_price
        },
        {
            id: "useful_life",
            label: "Useful life [years]",
            tooltip: "Lifetime of the system in years",
            step: "1",
            value: formData.useful_life,
            icon: RiHourglassLine,
            errors: state.errors?.useful_life
        }
    ]
}


// Advanced input fields for the form
export function get_advanced_input_fields({formData, state}: {formData: FinData, state: FormState}) {

    return [
        {
            id: "module_deg",
            label: "Module degradation [%]",
            tooltip: "Annual degradation of the PV generation in percent",
            step: "0.1",
            value: formData.module_deg,
            icon: RiArrowRightDownLine,
            errors: state.errors?.module_deg
        },
        {
            id: "inflation",
            label: "Inflation [%]",
            tooltip: "Annual inflation rate in percent",
            step: "0.1",
            value: formData.inflation,
            icon: RiFundsLine,
            errors: state.errors?.inflation
        },
        {
            id: "op_cost",
            label: "Operation cost [%]",
            tooltip: "Annual operation cost in percent of the total investment. Includes maintenance, insurance, etc.",
            step: "0.1",
            value: formData.op_cost,
            icon: RiToolsLine,
            errors: state.errors?.op_cost
        },
        {
            id: "down_payment",
            label: "Down payment [%]",
            tooltip: "Initial payment in percent of the total investment",
            step: "0.1",
            value: formData.down_payment,
            icon: RiCurrencyLine,
            errors: state.errors?.down_payment
        },
        {
            id: "pay_off_rate",
            label: "Pay off rate [%]",
            tooltip: "Annual pay off rate of the loan in percent",
            step: "0.1",
            value: formData.pay_off_rate,
            icon: RiHandCoinLine,
            errors: state.errors?.pay_off_rate
        },
        {
            id: "interest_rate",
            label: "Interest rate [%]",
            tooltip: "Annual interest rate of the loan in percent",
            step: "0.1",
            value: formData.interest_rate,
            icon: RiBankLine,
            errors: state.errors?.interest_rate
        }
    ]
}
