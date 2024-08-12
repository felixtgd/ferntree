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
import { ModelData, FormState } from '@/utils/definitions';

import { useFormStatus, useFormState } from 'react-dom'

import { useState } from 'react'; // TEMPORARY make server component later!!!

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" icon={RiSaveLine} disabled={pending}>
      Save Model
    </Button>
  )
}

export function ModelForm() {

  const defaultModelData: ModelData = {
    model_name: 'Aarau_10_10',
    location: 'Aarau',
    electr_cons: 6000,
    roof_incl: 0,
    roof_azimuth: 0,
    peak_power: 10,
    battery_cap: 10,
  };

  const [formData, setFormData] = useState(defaultModelData);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormData({ ...formData, [name]: value });
  };

  const initialState : FormState = { message: null, errors: {} };
  const [state, formAction] = useFormState(submitModel, initialState);

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
              onChange={handleChange}
              value = {formData.model_name}
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
              onChange={handleChange}
              value = {formData.location}
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
              onValueChange={
                (value: string) => {
                  setFormData({ ...formData, roof_incl: parseInt(value) });
                }
              }
              value = {formData.roof_incl.toString()}
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
              onValueChange={
                (value: string) => {
                  setFormData({ ...formData, roof_azimuth: parseInt(value) });
                }
              }
              value = {formData.roof_azimuth.toString()}
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
              onChange = {handleChange}
              value = {formData.electr_cons}
              placeholder="4,000"
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
              placeholder="10"
              icon={RiSunLine}
              onChange={handleChange}
              value = {formData.peak_power}
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
              placeholder="10"
              icon={RiBattery2ChargeLine}
              onChange={handleChange}
              value = {formData.battery_cap}
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
