/*
 *  vapourware.cpp
 *  Cocoa OpenGL
 *
 *  Created by gabriel on 20/09/2009.
 *  Copyright 2009 Gabriel Lee. All rights reserved.
 *
 */

#include "vapourword.h"
#import <OpenGL/gl.h>
#import <OpenGL/glext.h>
#import <OpenGL/glu.h>
#include "math.h"
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

//#import "GLString.h"

char* LoremIpsum = "Lorem ipsum dolor sit amet consectetur adipiscing elit Sed in augue id libero porta aliquet Morbi egestas est non enim tincidunt vestibulum Aliquam erat volutpat Vestibulum sed pretium magna In rutrum pharetra elit non sagittis massa rutrum quis Maecenas non dui augue eget scelerisque elit Nulla at lorem vel lectus pulvinar ultricies Praesent nec arcu orci Mauris blandit libero risus Duis quis mauris ac augue auctor eleifend ut id quam Donec vel diam ultricies elit dictum volutpat eget eu lorem Nunc facilisis ullamcorper commodo Morbi nisl risus viverra at tempus eget viverra vitae arcuAliquam leo lectus iaculis quis sollicitudin et sagittis condimentum enim Nulla vitae adipiscing magna Sed fringilla dapibus risus vel lobortis In velit sapien mollis sit amet sodales vel commodo sit amet dolor In augue diam volutpat vel vulputate id ullamcorper a quam Nam sodales pretium ante id lobortis sapien luctus ut Maecenas eget iaculis justo Nam placerat eros vel laoreet facilisis sapien lectus tempus nisl at ultricies nulla erat eu massa Nam ac urna ut justo blandit iaculis Nam justo dui tempor in adipiscing pulvinar mattis non tellus Pellentesque tincidunt purus eu libero mattis sed tincidunt odio rutrum Nam ultricies commodo suscipit Lorem ipsum dolor sit amet consectetur adipiscing elit Vestibulum sapien velit viverra non elementum nec euismod et nulla Nulla vel ligula at ante varius porttitor Suspendisse eget enim at lacus imperdiet consequat Sed eu arcu tortor Sed euismod placerat odio ac lacinia augue ornare semper Cras viverra mattis lacus a vulputate Mauris dapibus leo euismod sem laoreet lobortis in sed";

bool error = false;

struct PAIR
{
	int idx;
	float weight;
	char word[64];
	float width;
	float height;
	float depth;
	float rot;
	float x;
	float y;
	float x1;
	float y1;
	float x2;
	float y2;
	float z;
	float r;
	float g;
	float b;
};

#define NUMBER_OF_PAIRS 128

PAIR pairs[NUMBER_OF_PAIRS];

void drawError ()
{
	glDisable(GL_DEPTH_TEST);
	glColor3f (1,0,0);
	glBegin (GL_QUADS);
	glVertex3f(-1,1,0);
	glVertex3f(1,1,0);
	glVertex3f(1,-1,0);
	glVertex3f(-1,-1,0);
	glEnd ();
}

void drawWord (int word)
{
	glDisable(GL_DEPTH_TEST);
	glColor3f (pairs[word].r,pairs[word].g,pairs[word].b);
	glBegin (GL_QUADS);
	glVertex3f(pairs[word].x1, pairs[word].y2, pairs[word].z);
	glVertex3f(pairs[word].x2, pairs[word].y2, pairs[word].z);
	glVertex3f(pairs[word].x2, pairs[word].y1, pairs[word].z);
	glVertex3f(pairs[word].x1, pairs[word].y1, pairs[word].z);
	glEnd ();

	glColor3f (1,0,0);
	glBegin (GL_LINE_LOOP);
	glVertex3f(pairs[word].x1, pairs[word].y2, pairs[word].z);
	glVertex3f(pairs[word].x2, pairs[word].y1, pairs[word].z);
	glVertex3f(pairs[word].x2, pairs[word].y2, pairs[word].z);
	glVertex3f(pairs[word].x1, pairs[word].y1, pairs[word].z);
	glEnd ();

	glColor3f (0,0,0);
	glBegin (GL_LINE_LOOP);
	glVertex3f(pairs[word].x1, pairs[word].y2, pairs[word].z);
	glVertex3f(pairs[word].x2, pairs[word].y2, pairs[word].z);
	glVertex3f(pairs[word].x2, pairs[word].y1, pairs[word].z);
	glVertex3f(pairs[word].x1, pairs[word].y1, pairs[word].z);
	glEnd ();

}

float GetRand()
{
	return (float)rand() / (float)RAND_MAX;
}

bool PlacePairCheckRange(int p, float x, float y, int rangeStart, int rangeEnd)
{
	float newx1 = x - (pairs[p].width / 2);
	float newy1 = y - (pairs[p].height / 2);
	float newx2 = x + (pairs[p].width / 2);
	float newy2 = y + (pairs[p].height / 2);
	for(int i = rangeStart; i <= rangeEnd; i++)
	{
		if(i == p)
			continue;
			
		//px is the new one, which should be smaller than ix
		//so p should fit into i so checking that none of ps
		//points are contained in i gives us a collx check
		
/*
		if((newx1 > pairs[i].x1) && (newx1 < pairs[i].x2) && (newy1 > pairs[i].y1) && (newy1 < pairs[i].y2))
			return false;
		if((newx2 > pairs[i].x1) && (newx2 < pairs[i].x2) && (newy1 > pairs[i].y1) && (newy1 < pairs[i].y2))
			return false;
		if((newx1 > pairs[i].x1) && (newx1 < pairs[i].x2) && (newy2 > pairs[i].y1) && (newy2 < pairs[i].y2))
			return false;
		if((newx2 > pairs[i].x1) && (newx2 < pairs[i].x2) && (newy2 > pairs[i].y1) && (newy2 < pairs[i].y2))
			return false;
		if((pairs[i].x1 > newx1) && (pairs[i].x1 < newx2) && (pairs[i].y1 > newy1) && (pairs[i].y1 < newy2))
			return false;
		if((pairs[i].x2 > newx1) && (pairs[i].x2 < newx2) && (pairs[i].y1 > newy1) && (pairs[i].y1 < newy2))
			return false;
		if((pairs[i].x1 > newx1) && (pairs[i].x1 < newx2) && (pairs[i].y2 > newy1) && (pairs[i].y2 < newy2))
			return false;
		if((pairs[i].x2 > newx1) && (pairs[i].x2 < newx2) && (pairs[i].y2 > newy1) && (pairs[i].y2 < newy2))
			return false;

		if((x > pairs[i].x1) && (x < pairs[i].x2) && (y > pairs[i].y1) && (y < pairs[i].y2))
			return false;
		if((pairs[i].x > newx1) && (pairs[i].x < newx2) && (pairs[i].y > newy1) && (pairs[i].y < newy2))
			return false;
*/
		if(!(((newx1 < pairs[i].x1) && (newx2 < pairs[i].x1)) || ((newx1 > pairs[i].x2) && (newx2 > pairs[i].x2))))
		{
			if(!(((newy1 < pairs[i].y1) && (newy2 < pairs[i].y1)) || ((newy1 > pairs[i].y2) && (newy2 > pairs[i].y2))))
			{
				return false;
			}
		}
		
	}
	pairs[p].x = x;
	pairs[p].y = y;
	pairs[p].x1 = newx1;
	pairs[p].y1 = newy1;
	pairs[p].x2 = newx2;
	pairs[p].y2 = newy2;
	return true;
}

float centerx = 0;
float centery = 0;

int TryToFit()
{
	float tryDistXStart = 150;
	float tryDistYStart = 150;
	float tryDistXChange = .1;
	float tryDistYChange = .1;
	PlacePairCheckRange(NUMBER_OF_PAIRS - 1, centerx, centery, 0, 0);
	int invi = 0;
	for(int i = NUMBER_OF_PAIRS - 2; i > -1; i--)
	{
		//place
		float tryDistX = tryDistXStart + (tryDistXChange * invi);
		float tryDistY = tryDistYStart + (tryDistYChange * invi);
		int t = 0;
		int tryHoriz = 2;
		for(t = 0; t < tryHoriz; t++)
		{
			if(PlacePairCheckRange(i, centerx + (tryDistX * (GetRand() - .5)), centery + (tryDistY * (GetRand() - .5)), i + 1, NUMBER_OF_PAIRS - 1))
			{
				break;
			}
		}
		if(t == tryHoriz)
		{
			pairs[i].rot = -90.0f;
			float tmp = pairs[i].width;
			pairs[i].width = pairs[i].height;
			pairs[i].height = tmp;
			for(; t < 1000; t++)
			{
				if(PlacePairCheckRange(i, centerx + (tryDistX * (GetRand() - .5)), centery + (tryDistY * (GetRand() - .5)), i + 1, NUMBER_OF_PAIRS - 1))
				{
					break;
				}
			}
		}
		if(t == 1000)
		{
			return 0;
		}
		
		//compact
		for(int t = 0; t < 100; t++)
		{
			float newx = ((pairs[i].x * (1000 - t)) + (t * centerx)) / 1000.0f;
			float newy = ((pairs[i].y * (1000 - t)) + (t * centery)) / 1000.0f;
			if(!PlacePairCheckRange(i, newx, newy, i + 1, NUMBER_OF_PAIRS - 1))
			{
				if(!PlacePairCheckRange(i, newx, pairs[i].y, i + 1, NUMBER_OF_PAIRS - 1))
				{
					if(!PlacePairCheckRange(i, pairs[i].x, newy, i + 1, NUMBER_OF_PAIRS - 1))
					{
						break;
					}
				}
			}
		}
		invi++;
	}
	return 1;
}

int Compact()
{
	for(int i = NUMBER_OF_PAIRS - 2; i > -1; i--)
	{
		for(int t = 0; t < 1000; t++)
		{
			float newx = ((pairs[i].x * (1000 - t)) + (t * centerx)) / 1000.0f;
			float newy = ((pairs[i].y * (1000 - t)) + (t * centery)) / 1000.0f;
			if(!PlacePairCheckRange(i, newx, newy, 0, NUMBER_OF_PAIRS - 1))
			{
				if(!PlacePairCheckRange(i, newx, pairs[i].y, 0, NUMBER_OF_PAIRS - 1))
				{
					if(!PlacePairCheckRange(i, pairs[i].x, newy, 0, NUMBER_OF_PAIRS - 1))
					{
						t = 1000;
						break;
					}
				}
			}
		}
	}
}

void RandomBruteForce()
{
	//try 1000 times and score based on total width and height
//	for(int bfc = 0; bfc < 1000; bfc++)
	{
		int ret = TryToFit();
		if(ret == 0)
		{
			error = true;
		}
//		Compact();
	}
}

void init()
{
	int pos = 0;
	float weight = .1f;
	float size_scale = 10;
	float squWeight;
	for(int i = 0; i < NUMBER_OF_PAIRS; i++)
	{
		weight += (GetRand() / 128);
		squWeight = (weight * weight) + .25;// * weight * weight;
		pairs[i].idx = i;
		pairs[i].weight = weight;
		pairs[i].width = ((GetRand() * 7) + 3) * (squWeight * size_scale);
//		pairs[i].width *= pairs[i].width;
//		pairs[i].width /= 22;
		pairs[i].height = (2) * (squWeight * size_scale);
//		pairs[i].height *= pairs[i].height;
//		pairs[i].height /= 22;
		pairs[i].depth = (2) * (squWeight * size_scale);
		pairs[i].rot = 0;
		pairs[i].x = 0;
		pairs[i].y = 0;
		pairs[i].z = 0;
		pairs[i].r = pairs[i].weight;
		pairs[i].g = 1;
		pairs[i].b = pairs[i].weight;

		memset(pairs[i].word,0,64);
		for(int j = 0; j < 64; j++)
		{
			if(LoremIpsum[pos] == 0)
				break;
				
			if(LoremIpsum[pos] != ' ')
			{
				pairs[i].word[j] = LoremIpsum[pos++];
			}
			else
			{
				pos++;
			}
		}
	}
	
	//scale weights to 1.0f
	//get total area
	//square weights to give a nice exponent
	squWeight = (weight * weight) + 1;// * weight * weight;
	float totalArea = 0;
	for(int i = 0; i < NUMBER_OF_PAIRS; i++)
	{
		pairs[i].width /= squWeight;
		pairs[i].height /= squWeight;
		pairs[i].weight /= weight;
		pairs[i].r /= weight;
		pairs[i].g = 1;
		pairs[i].b /= weight;
		
		totalArea += (pairs[i].width * pairs[i].height);
	}
/*
	//scale by total area 
	for(int i = 0; i < NUMBER_OF_PAIRS; i++)
	{
		pairs[i].width /= weight;
		pairs[i].height /= weight;
		pairs[i].weight /= weight;
		pairs[i].r /= weight;
		pairs[i].g = 1;
		pairs[i].b /= weight;
		
		totalArea += (pairs[i].width * pairs[i].height);
	}
*/

/*	//place in reverse order starting at the center
	float posx = 0;
	float posy = 0;
	for(int i = NUMBER_OF_PAIRS - 1; i > -1; i--)
	{
		pairs[i].y = posy;
		posy += pairs[i].height;
	}*/
	
	RandomBruteForce();

	//centralise
	float minx = pairs[NUMBER_OF_PAIRS - 1].x;
	float miny = pairs[NUMBER_OF_PAIRS - 1].y;
	float maxx = pairs[NUMBER_OF_PAIRS - 1].x + pairs[NUMBER_OF_PAIRS - 1].width;
	float maxy = pairs[NUMBER_OF_PAIRS - 1].y + pairs[NUMBER_OF_PAIRS - 1].height;
	for(int i = NUMBER_OF_PAIRS - 2; i > -1; i--)
	{
		if(pairs[i].x < minx)
		{
			minx = pairs[i].x;
		}
		if(pairs[i].y < miny)
		{
			miny = pairs[i].y;
		}

		if((pairs[i].x + pairs[i].width) > maxx)
		{
			maxx = (pairs[i].x + pairs[i].width);
		}
		if((pairs[i].y + pairs[i].height) > maxy)
		{
			maxy = (pairs[i].y + pairs[i].height);
		}
	}
	
	float shiftx = ((-((maxx - minx) / 2)) - ((maxx + minx) / 2));
	float shifty = ((-((maxy - miny) / 2)) - ((maxy + miny) / 2));
	for(int i = NUMBER_OF_PAIRS - 1; i > -1; i--)
	{
		pairs[i].x += shiftx;
		pairs[i].y += shifty;
	}
}

void render()
{
	if(!error)
	{
		for(int i = NUMBER_OF_PAIRS - 1; i > -1; i--)
		{
			drawWord(i);
		}
	}
	else
	{
		drawError();
	}
}

extern "C"
{
	void _render()
	{
		render();
	}

	void _init()
	{
		init();
	}
};
