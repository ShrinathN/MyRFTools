#include "main.h"
#define ERROR_LED HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET)
#define SPI_START HAL_GPIO_WritePin(SPI_SS_GPIO_Port, SPI_SS_Pin, GPIO_PIN_RESET)
#define SPI_STOP HAL_GPIO_WritePin(SPI_SS_GPIO_Port, SPI_SS_Pin, GPIO_PIN_SET)

#define MAX_U8 0xff
typedef unsigned char U8;


SPI_HandleTypeDef hspi1;

UART_HandleTypeDef huart1;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_SPI1_Init(void);
static void MX_USART1_UART_Init(void);


void RF96_write(U8 * data, U8 length)
{
  U8 status = MAX_U8;
  SPI_START;
  status = HAL_SPI_Transmit(&hspi1, data, length, 100);
  if(status != HAL_OK)
  {
    ERROR_LED;
  }
  SPI_STOP;
}

U8 RF96_read(U8 address)
{
  U8 data = MAX_U8;
  SPI_START;
  HAL_SPI_Transmit(&hspi1, (U8[]){address}, 1, 100);
  HAL_SPI_Receive(&hspi1, &data, 1, 100);
  SPI_STOP;
  return data;
}

U8 buffer[110];
U8 length, counter;
int main(void)
{
  HAL_Init();
  SystemClock_Config();

  MX_GPIO_Init();
  MX_SPI1_Init();
  MX_USART1_UART_Init();

  RF96_write((U8[]){(1 << 7) | 0x1, 0x80}, 2);
  //waiting for sleep mode to take over
  HAL_Delay(10);
  //setting frequency
  RF96_write((U8[]){(1 << 7) | 0x6, 217, 0, 0}, 4);
  //setting output power limited upto 20dBm, ramp up and down times in FSK as 40us
  RF96_write((U8[]){(1 << 7) | 0x9, 0xff, 0b1001}, 3);
  //setting LNA gain as max, default current
  RF96_write((U8[]){(1 << 7) | 0xc, 0b00100000}, 2);
  //setting rx and tx base addresses
  RF96_write((U8[]){(1 << 7) | 0xe, 0x0,0x0}, 3);
  //setting signal bandwidth as 500KHz and error coding rate as 4/8, and implicit header mode
  RF96_write((U8[]){(1 << 7) | 0x1d, 0b10011001}, 2);
  //setting spread factor as 12, packet mode
  RF96_write((U8[]){(1 << 7) | 0x1e, 0b11000011}, 2);
  //setting preamble length as 8
  RF96_write((U8[]){(1 << 7) | 0x20, 0, 8}, 3);
  //setting in mobile node
  RF96_write((U8[]){(1 << 7) | 0x26, (1 << 3) | (1 << 2)}, 2);

  //setting DIO to pulse at RxDone
  RF96_write((U8[]){(1 << 7) | 0x40, 0}, 2);

  //setting payload length at 5 bytes
  RF96_write((U8[]){(1 << 7) | 0x22, 0x5}, 2);

  //standby mode
  RF96_write((U8[]){(1 << 7) | 0x1, (1 << 7) | 1}, 2);


  //wait 10ms
  HAL_Delay(10);

  //receive mode continuous
   RF96_write((U8[]){(1 << 7) | 0x1, (1 << 7) | 0b101}, 2);

  HAL_Delay(10);
  while(1)
  {
    buffer[0] = RF96_read(0x1); //main register
    buffer[1] = RF96_read(0x12); //IRQ register
    RF96_write((U8[]){(1 << 7) | 0x12, buffer[1]}, 2); //clearing IRQ
    if(buffer[1] == 0x40) //meaning successfully received byte
    {
      HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);

      buffer[2] = RF96_read(0x13); //number of payload bytes received
      buffer[3] = RF96_read(0x10); //start address of packet
      buffer[4] = RF96_read(0x1a); //last packet RSSI
      RF96_write((U8[]){(1 << 7) | 0x0d, buffer[3]}, 2); //writing starting byte

      //reading data bytes
      SPI_START;
      HAL_SPI_Transmit(&hspi1, (U8[]){0x0}, 1, 100);
      HAL_SPI_Receive(&hspi1, (buffer + 5), buffer[2], 100);
      SPI_STOP;


      HAL_UART_Transmit(&huart1, buffer, buffer[2] + 5, 100);
    }
  }
}

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the CPU, AHB and APB busses clocks
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB busses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_4;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 10;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */

  /* USER CODE END SPI1_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(SPI_SS_GPIO_Port, SPI_SS_Pin, GPIO_PIN_SET);

  /*Configure GPIO pin : LED_Pin */
  GPIO_InitStruct.Pin = LED_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_GPIO_Port, &GPIO_InitStruct);

  //PA0 as input
  GPIO_InitStruct.Pin = GPIO_PIN_0;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : SPI_SS_Pin */
  GPIO_InitStruct.Pin = SPI_SS_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(SPI_SS_GPIO_Port, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
