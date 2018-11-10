
instance_alpha = {
					'type': 'box',
					'name': 'test',
					'x_max': 128, 
					'x_min': 48,
					'y_min': 97,
					'y_max': 128,
					'trackid': 'hasldk123'
					}

instance_bravo = {
					'type': 'box',
					'name': 'test',
					'x_max': 128, 
					'x_min': 1,
					'y_min': 1,
					'y_max': 128,
					'trackid': '10123980980123'
				}


frame_packet = {'instance_list' : [instance_alpha, instance_bravo],
				'future' : 'future'
				}

image_packet = {'instance_list' : [instance_alpha, instance_bravo],
				  'media' : {
					  'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
					  'type' : 'image'
					  }
				  }

video_packet = {'frame_packet_map' : {
					0 : frame_packet,
					6 : frame_packet,
					9 : frame_packet
				},
				'media' : {
					'url' : "https://storage.googleapis.com/diffgram-002/projects/videos/45/74?GoogleAccessId=storage%40diffgram-001.iam.gserviceaccount.com&Signature=VPb9ecqssGhSC0NgDeDLrwNSQze3s7KbyufsnbxZbelfZs7tgbeN0h2DObRrUZmixA6x6UPyVEE%2FB6u4u48Ds6YpE4zaSWFBotRBFZumWf2hfo1JBFxP04JUReSQlZ%2BgQi5I%2BdU%2FRVD1zuuV0K4l3%2FMldquLcuXXNotyZXbp0XvNtywg6ciluQ8cOwF3TFlXuddqZGFiSr177vu0oO5tcIzFJUvyKPjuHkjxzxJeOO9P1LuuhJTa72w9W0uvTLrePHknAWF6U1SLOw%2ByfpJmt5CLZNxFpHi6lsUgWeuiH1ri%2Bvyj2d9M3jjm8iCoejPRWICQwj1wJL4KIJWDZ0sraQ%3D%3D&Expires=1544379489&response-content-disposition=attachment%3B+filename%3D74",
					'type' : 'video'
					}
				}
