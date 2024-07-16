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

import { submitForm } from './actions';
import { useFormStatus } from 'react-dom'

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

  const [formData] = useState({
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

  return (
    <Card
      className="sm:mx-auto sm:max-w-lg"
      decoration="top"
      decorationColor="blue-300"
    >
      <form action={submitForm}>
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
              // onChange={handleChange}
              value = {formData.location}
              placeholder="Enter location"
            />
          </div>
        </div>

        {/* Annual electricity consumption */}
        <div className="mb-4">
          <label htmlFor="electr_cons" className="mb-2 block text-sm font-medium">
            Electricity consumption [kWh/a]
          </label>
          <div className="relative">
            <NumberInput
              id="electr_cons"
              name="electr_cons"
              step="1"
              icon={RiLightbulbFlashLine}
              // onChange = {handleChange}
              value = {formData.electr_cons}
              placeholder="300,000"
            />
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
              // onValueChange={handleRoofInclChange}
              value = {formData.roof_incl.toString()}
            >
              <SelectItem value="0">0°</SelectItem>
              <SelectItem value="30">30°</SelectItem>
              <SelectItem value="45">45°</SelectItem>
            </Select>
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
                // onValueChange={handleRoofAzChange}
                value = {formData.roof_azimuth.toString()}
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
        </div>

        {/* PV Peak Power */}
        <div className="mb-4">
          <label htmlFor="peak_power" className="mb-2 block text-sm font-medium">
            PV peak power [kWp]
          </label>
            <div className="relative">
              <NumberInput
                id="peak_power"
                name="peak_power"
                step="0.1"
                placeholder="10"
                icon={RiSunLine}
                // onChange={handleChange}
                value = {formData.peak_power}
              />
            </div>
        </div>

        {/* Battery capacity */}
        <div className="mb-4">
          <label htmlFor="battery_cap" className="mb-2 block text-sm font-medium">
            Battery capacity [kWh]
          </label>
            <div className="relative">
              <NumberInput
                id="battery_cap"
                name="battery_cap"
                step="0.1"
                placeholder="10"
                icon={RiBattery2ChargeLine}
                // onChange={handleChange}
                value = {formData.battery_cap}
              />
            </div>
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
                placeholder="35"
                icon={RiCoinsLine}
                // onChange={handleChange}
                value = {formData.electr_price}
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
                placeholder="20"
                icon={RiCurrencyLine}
                // onChange={handleChange}
                value = {formData.down_payment}
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
                placeholder="5"
                icon={RiHandCoinLine}
                // onChange={handleChange}
                value = {formData.pay_off_rate}
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
                placeholder="3"
                icon={RiBankLine}
                // onChange={handleChange}
                value = {formData.interest_rate}
              />
            </div>
        </div>

        <div className="mt-6 flex justify-center gap-4">
          <SubmitButton />
        </div>
      </form>
    </Card>
  );
}
