using System;
using System.Drawing;

namespace OneWeekend.Image
{
    public class BitmapGenerator
    {
        public static void GenerateAndSaveImage()
        {
            try
            {
                Bitmap bmp = new Bitmap(200, 200, System.Drawing.Imaging.PixelFormat.Format32bppPArgb);
                bmp = ChangeColor(bmp);
                bmp.Save("image.jpg");
            }
            catch (System.Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }
        public static Bitmap ChangeColor(Bitmap scrBitmap)
        {
            Color newColor = Color.Coral;
            for (int i = 0; i < scrBitmap.Width; i++)
            {
                for (int j = 0; j < scrBitmap.Height; j++)
                {
                    scrBitmap.SetPixel(i, j, newColor);
                }
            }
            return scrBitmap;
        }
    }
}