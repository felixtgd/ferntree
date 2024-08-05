'use client'

import { Button, Dialog, DialogPanel } from '@tremor/react';
import React from 'react';
import { ModelForm } from './model-form';

export function ModelFormDialog() {
  const [isOpen, setIsOpen] = React.useState(false);
  return (
    <>
    <Button className="mx-auto block" onClick={() => setIsOpen(true)}>Create Model</Button>
    <Dialog open={isOpen} onClose={(val) => setIsOpen(val)} static={true}>
      <DialogPanel>
        <div className="flex justify-between items-center">
            <h3 className="mx-auto text-lg font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                Create a new model
            </h3>

            <Button
                variant="light"
                className="flex items-center"
                onClick={() => setIsOpen(false)}
            >
                Cancel
            </Button>
        </div>

        <ModelForm />

      </DialogPanel>
    </Dialog>
    </>
  );
}
