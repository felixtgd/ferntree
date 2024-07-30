'use client'

import { Card, NumberInput, Select, SelectItem, TextInput, Button } from '@tremor/react';
import {
  RiArrowUpWideLine,
  RiBankLine,
  RiBattery2ChargeLine,
  RiCalculatorLine,
  RiCoinsLine,
  RiCompassLine,
  RiCurrencyLine,
  RiHandCoinLine,
  RiHome4Line,
  RiLightbulbFlashLine,
  RiSunLine
} from '@remixicon/react';

import { State, submitForm } from './actions';
import { useFormStatus, useFormState } from 'react-dom'

import { useState } from 'react'; // TEMPORARY make server component later!!!

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" icon={RiCalculatorLine} disabled={pending}>
      Calculate System
    </Button>
  )
}

export function PvForm() {

  const [formData, setFormData] = useState({
    location: 'Aarau',
    electr_cons: 6000,
    roof_incl: 0,
    roof_azimuth: 0,
    peak_power: 10,
    battery_cap: 10,
    electr_price: 35,
    down_payment: 20,
    pay_off_rate: 5,
    interest_rate: 3,
  }); // put this in a data model?

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleRoofInclChange = (value: string) => {
    setFormData({ ...formData, roof_incl: parseInt(value) });
  }

  const handleRoofAzChange = (value: string) => {
    setFormData({ ...formData, roof_azimuth: parseInt(value) });
  }

  const initialState : State = { message: null, errors: {} };
  const [state, formAction] = useFormState(submitForm, initialState);

  return (
    <Card
      className="sm:mx-auto sm:max-w-lg"
      decoration="top"
      decorationColor="blue-300"
    >
      <form action={formAction}>
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
              onValueChange={handleRoofInclChange}
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
              onValueChange={handleRoofAzChange}
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

        {/* Electricity price */}
        <div className="mb-4">
          <label htmlFor="electr_price" className="mb-2 block text-sm font-medium">
            Electricity price <span className="text-gray-400"> cents/kWh </span>
          </label>
          <div className="relative">
            <NumberInput
              id="electr_price"
              name="electr_price"
              step="0.1"
              placeholder="35"
              icon={RiCoinsLine}
              onChange={handleChange}
              value = {formData.electr_price}
              required
            />
          </div>
          <div id="electr_price-error" aria-live="polite" aria-atomic="true">
            {state.errors?.electr_price &&
              state.errors.electr_price.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Down payment */}
        <div className="mb-4">
          <label htmlFor="down_payment" className="mb-2 block text-sm font-medium">
            Down payment <span className="text-gray-400"> % </span>
          </label>
          <div className="relative">
            <NumberInput
              id="down_payment"
              name="down_payment"
              step="0.1"
              placeholder="20"
              icon={RiCurrencyLine}
              onChange={handleChange}
              value = {formData.down_payment}
              required
            />
          </div>
          <div id="down_payment-error" aria-live="polite" aria-atomic="true">
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
            Pay off rate <span className="text-gray-400"> % </span>
          </label>
          <div className="relative">
            <NumberInput
              id="pay_off_rate"
              name="pay_off_rate"
              step="0.1"
              placeholder="5"
              icon={RiHandCoinLine}
              onChange={handleChange}
              value = {formData.pay_off_rate}
              required
            />
          </div>
          <div id="pay_off_rate-error" aria-live="polite" aria-atomic="true">
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
            Interest rate <span className="text-gray-400"> % </span>
          </label>
          <div className="relative">
            <NumberInput
              id="interest_rate"
              name="interest_rate"
              step="0.1"
              placeholder="3"
              icon={RiBankLine}
              onChange={handleChange}
              value = {formData.interest_rate}
              required
            />
          </div>
          <div id="interest_rate-error" aria-live="polite" aria-atomic="true">
            {state.errors?.interest_rate &&
              state.errors.interest_rate.map((error: string) => (
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
    </Card>
  );
}
