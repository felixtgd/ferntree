'use client'

import { Button, Dialog, DialogPanel } from '@tremor/react';
import { useState } from 'react';
import { ModelForm } from './model-form';

export function ModelFormDialog({num_models}: {num_models: number}) {
  const [isOpen, setIsOpen] = useState(false);

  let tooltip;
  if (num_models >= 5) {
    tooltip = 'You have reached the maximum number of models. Delete a model to create a new one.';
  } else {
    tooltip = 'Create a new model';
  }

  return (
    <>
    <Button
      className="block"
      onClick={() => setIsOpen(true)}
      tooltip={tooltip}
      disabled={num_models >= 5}
    >
      Create Model
    </Button>
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
                Close
            </Button>
        </div>

        <ModelForm setIsOpen={setIsOpen} />

      </DialogPanel>
    </Dialog>
    </>
  );
}
