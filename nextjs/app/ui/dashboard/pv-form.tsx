/* Create a form to input the following data for the PV system:
location (text),
annual electricity consumption in kWh (number),
roof inclination and orientation in degrees (number),
system size in kWp (number),
battery capacity in kWh (number),
electricity price in cents/kWh (number),
down payment in percent (number),
pay off rate in percent (number).*/

'use client';

import Link from 'next/link';
import {
  CheckIcon,
  ClockIcon,
  CurrencyDollarIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/app/ui/button';
import { useFormState } from 'react-dom';

export default function Form() {

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log('Form submitted');
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="rounded-md bg-gray-200 p-4 md:p-4 w-64">

        {/* Location */}
        <div className="mb-4">
          <label htmlFor="location" className="mb-2 block text-sm font-medium">
            Location
          </label>
          <div className="relative">
            <input
              id="location"
              name="location"
              type="text"
              placeholder="Enter location"
              className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
            />
          </div>
        </div>

        {/* Annual electricity consumption */}
        <div className="mb-4">
          <label htmlFor="electr_cons" className="mb-2 block text-sm font-medium">
            Electricity consumption [kWh/a]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="electr_cons"
                name="electr_cons"
                type="number"
                step="0.01"
                placeholder="300,000"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Roof inclination */}
        <div className="mb-4">
          <label htmlFor="roof_incl" className="mb-2 block text-sm font-medium">
            Roof inclination
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <select
                id="roof_incl"
                name="roof_incl"
                className="peer block w-full cursor-pointer rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
                defaultValue=""
              >
                <option value="" disabled>
                  Select roof inclination
                </option>
                <option value="0">0°</option>
                <option value="30">30°</option>
                <option value="45">45°</option>
              </select>
            </div>
          </div>
        </div>

        {/* Roof orientation */}
        <div className="mb-4">
          <label htmlFor="roof_azimuth" className="mb-2 block text-sm font-medium">
            Roof orientation
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <select
                id="roof_azimuth"
                name="roof_azimuth"
                className="peer block w-full cursor-pointer rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
                defaultValue=""
              >
                <option value="" disabled>
                  Select roof orientation
                </option>
                <option value="0">South</option>
                <option value="-45">South-East</option>
                <option value="45">South-West</option>
                <option value="-90">East</option>
                <option value="90">West</option>
                <option value="-135">North-East</option>
                <option value="135">North-West</option>
                <option value="180">North</option>
              </select>
            </div>
          </div>
        </div>

        {/* PV Peak Power */}
        <div className="mb-4">
          <label htmlFor="peak_power" className="mb-2 block text-sm font-medium">
            PV peak power [kWp]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="peak_power"
                name="peak_power"
                type="number"
                step="0.01"
                placeholder="10"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Battery capacity */}
        <div className="mb-4">
          <label htmlFor="battery_cap" className="mb-2 block text-sm font-medium">
            Battery capacity [kWh]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="battery_cap"
                name="battery_cap"
                type="number"
                step="0.01"
                placeholder="10"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Electricity price */}
        <div className="mb-4">
          <label htmlFor="elec_price" className="mb-2 block text-sm font-medium">
            Electricity price [cents/kWh]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="elec_price"
                name="elec_price"
                type="number"
                step="0.01"
                placeholder="35"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Down payment */}
        <div className="mb-4">
          <label htmlFor="down_payment" className="mb-2 block text-sm font-medium">
            Down payment [%]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="down_payment"
                name="down_payment"
                type="number"
                step="0.01"
                placeholder="20"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Pay off rate */}
        <div className="mb-4">
          <label htmlFor="pay_off_rate" className="mb-2 block text-sm font-medium">
            Pay off rate [%]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="pay_off_rate"
                name="pay_off_rate"
                type="number"
                step="0.01"
                placeholder="5"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Interest rate */}
        <div className="mb-4">
          <label htmlFor="interest_rate" className="mb-2 block text-sm font-medium">
            Interest rate [%]
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="interest_rate"
                name="interest_rate"
                type="number"
                step="0.01"
                placeholder="3"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-center gap-4">
          <Button type="submit">Calculate System</Button>
        </div>

      </div>

    </form>
  );
}
