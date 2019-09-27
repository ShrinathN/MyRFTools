#include "main.h"
#include "stm32f1xx_it.h"

#define READ_PIN HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0)

extern TIM_HandleTypeDef htim2;
extern TIM_HandleTypeDef htim1;
extern UART_HandleTypeDef huart1;

void NMI_Handler(void)
{

}

void HardFault_Handler(void)
{

  while (1)
  {
  }
}

void MemManage_Handler(void)
{
  while (1)
  {
  }
}


void BusFault_Handler(void)
{
  while (1)
  {
  }
}


void UsageFault_Handler(void)
{
  while (1)
  {
  }
}

/**
  * @brief This function handles System service call via SWI instruction.
  */
void SVC_Handler(void)
{

}


void DebugMon_Handler(void)
{
}


void PendSV_Handler(void)
{
}

void SysTick_Handler(void)
{
}


void TIM1_UP_IRQHandler(void)
{
  HAL_TIM_IRQHandler(&htim1);
}

char buffer[3] = {0xff,0xff,'\n'};

void TIM2_IRQHandler(void)
{
  static unsigned char x;
  x = READ_PIN;
  if(x)
  {
    HAL_UART_Transmit(&huart1, "1", 1,1);
  }
  else
  {
    HAL_UART_Transmit(&huart1, "0", 1, 1);
  }

  // static __UINT8_TYPE__ counter = 0, positives = 0;
  // HAL_TIM_IRQHandler(&htim2);
  // counter++;
  // if(counter >= 20)
  // {
  //   buffer[0] = 48 + (positives / 10);
  //   buffer[1] = 48 + (positives % 10);
  //   HAL_UART_Transmit(&huart1, buffer, 3, 100);
  //   counter = 0;
  //   positives = 0;
  // }
  // positives += HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0)==0?0:1;
}