'use client'

import { NumberInput, Select, SelectItem, TextInput, Button } from '@tremor/react';
import {
  RiArrowUpWideLine,
  RiBattery2ChargeLine,
  RiCompassLine,
  RiHome4Line,
  RiLightbulbFlashLine,
  RiPriceTag3Line,
  RiSaveLine,
  RiSunLine
} from '@remixicon/react';
import { submitModel } from './actions';
import { FormState } from '@/app/utils/definitions';
import { useFormStatus, useFormState } from 'react-dom'
import { useEffect } from 'react'


function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <Button
      type="submit"
      icon={RiSaveLine}
      disabled={pending}
    >
      Save Model
    </Button>
  )
}

export function ModelForm({setIsOpen}: {setIsOpen: (val: boolean) => void}) {

  const initialState : FormState = { message: null, errors: {} };
  const [state, formAction] = useFormState(submitModel, initialState);

  // Close form dialog after successful submission
  useEffect(() => {
    if (state.message === 'success') {
      setIsOpen(false);
    }
  }, [state, setIsOpen]);

  return (
      <form action={formAction}>
        {/* Model Name */}
        <div className="mb-4">
          <label htmlFor="model_name" className="mb-2 block text-sm font-medium">
            Model name
          </label>
          <div className="relative">
            <TextInput
              id="model_name"
              name="model_name"
              type="text"
              icon={RiPriceTag3Line}
              placeholder="Enter model name"
              required
            />
          </div>
          <div id="model_name-error" aria-live="polite" aria-atomic="true">
            {state.errors?.model_name &&
              state.errors.model_name.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Location */}
        <div className="mb-4">
          <label htmlFor="location" className="mb-2 block text-sm font-medium">
            Location
          </label>
          <div className="relative">
            <TextInput
              id="location"
              name="location"
              type="text"
              icon={RiHome4Line}
              placeholder="Enter location"
              required
            />
          </div>
          <div id="location-error" aria-live="polite" aria-atomic="true">
            {state.errors?.location &&
              state.errors.location.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Roof inclination */}
        <div className="mb-4">
          <label htmlFor="roof_incl" className="mb-2 block text-sm font-medium">
            Roof inclination
          </label>
          <div className="relative">
            <Select
              id="roof_incl"
              name="roof_incl"
              icon={RiArrowUpWideLine}
              required
            >
              <SelectItem value="0">0°</SelectItem>
              <SelectItem value="30">30°</SelectItem>
              <SelectItem value="45">45°</SelectItem>
            </Select>
          </div>
          <div id="roof_incl-error" aria-live="polite" aria-atomic="true">
            {state.errors?.roof_incl &&
              state.errors.roof_incl.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Roof orientation */}
        <div className="mb-4">
          <label htmlFor="roof_azimuth" className="mb-2 block text-sm font-medium">
            Roof orientation
          </label>
          <div className="relative">
            <Select
              id="roof_azimuth"
              name="roof_azimuth"
              icon={RiCompassLine}
              required
            >
              <SelectItem value="0">South</SelectItem>
              <SelectItem value="-45">South-East</SelectItem>
              <SelectItem value="45">South-West</SelectItem>
              <SelectItem value="-90">East</SelectItem>
              <SelectItem value="90">West</SelectItem>
              <SelectItem value="-135">North-East</SelectItem>
              <SelectItem value="135">North-West</SelectItem>
              <SelectItem value="180">North</SelectItem>
            </Select>
          </div>
          <div id="roof_azimuth-error" aria-live="polite" aria-atomic="true">
            {state.errors?.roof_azimuth &&
              state.errors.roof_azimuth.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Annual electricity consumption */}
        <div className="mb-4">
          <label htmlFor="electr_cons" className="mb-2 block text-sm font-medium">
            Electricity consumption <span className="text-gray-400"> kWh/a </span>
          </label>
          <div className="relative">
            <NumberInput
              id="electr_cons"
              name="electr_cons"
              step="1"
              icon={RiLightbulbFlashLine}
              placeholder="Set annual consumption in kWh, e.g. 3,000"
              required
            />
          </div>
          <div id="electr_cons-error" aria-live="polite" aria-atomic="true">
            {state.errors?.electr_cons &&
              state.errors.electr_cons.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* PV Peak Power */}
        <div className="mb-4">
          <label htmlFor="peak_power" className="mb-2 block text-sm font-medium">
            PV peak power <span className="text-gray-400"> kWp </span>
          </label>
          <div className="relative">
            <NumberInput
              id="peak_power"
              name="peak_power"
              step="0.1"
              placeholder="Set peak power in kWp, e.g. 10"
              icon={RiSunLine}
              required
            />
          </div>
          <div id="peak_power-error" aria-live="polite" aria-atomic="true">
            {state.errors?.peak_power &&
              state.errors.peak_power.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Battery capacity */}
        <div className="mb-4">
          <label htmlFor="battery_cap" className="mb-2 block text-sm font-medium">
            Battery capacity <span className="text-gray-400"> kWh </span>
          </label>
          <div className="relative">
            <NumberInput
              id="battery_cap"
              name="battery_cap"
              step="0.1"
              placeholder="Set capacity in kWh, e.g. 10"
              icon={RiBattery2ChargeLine}
              required
            />
          </div>
          <div id="battery_cap-error" aria-live="polite" aria-atomic="true">
            {state.errors?.battery_cap &&
              state.errors.battery_cap.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
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
